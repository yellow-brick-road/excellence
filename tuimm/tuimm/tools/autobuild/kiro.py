"""kiro.py — ACP client for kiro-cli agent subprocess management.

Speaks JSON-RPC 2.0 over stdio to kiro-cli acp. Handles initialize,
session creation, prompting, and cleanup.

Based on proven lib/acp.py from poc.newspaper and b2c-frontend migration.

Usage:
    agent = AcpAgent("tuimm_default", "claude-sonnet-4.6", cwd="/path")
    text = agent.prompt("Implement the feature...", timeout=300)
    agent.close()
"""

import json, os, select, signal, subprocess, sys, time

# ── logd integration (optional) ─────────────────────────────────────────────

_log = None


def _get_log():
    global _log
    if _log is None:
        try:
            sys.path.insert(0, os.path.expanduser("~/.kiro/tuimm/tools/logd"))
            from loglib import get_logger
            _log = get_logger("autobuild.kiro")
        except Exception:
            _log = False
    return _log if _log else None


class AcpError(Exception):
    pass


class AcpAgent:
    """Manages a single kiro-cli ACP subprocess."""

    def __init__(self, agent: str, model: str, cwd: str):
        self._cwd = cwd
        self._id = 0
        self._session_id = None

        env = os.environ.copy()
        uid = env.get("LOGD_UID")
        if uid:
            env["LOGD_UID"] = uid

        self.proc = subprocess.Popen(
            ["kiro-cli", "acp", "--agent", agent, "--model", model, "--trust-all-tools"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            cwd=cwd, start_new_session=True, env=env,
        )
        try:
            self._initialize()
            self._new_session(cwd)
        except Exception:
            self.close()
            raise

    # ── Protocol helpers ──────────────────────────────────────────

    def _next_id(self):
        self._id += 1
        return self._id

    def _send(self, method, params, *, is_request=True):
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if is_request:
            rid = self._next_id()
            msg["id"] = rid
        else:
            rid = None
        self.proc.stdin.write(json.dumps(msg).encode() + b"\n")
        self.proc.stdin.flush()
        return rid

    def _respond(self, rid, result):
        msg = {"jsonrpc": "2.0", "id": rid, "result": result}
        self.proc.stdin.write(json.dumps(msg).encode() + b"\n")
        self.proc.stdin.flush()

    def _readline(self, timeout=10):
        ready, _, _ = select.select([self.proc.stdout], [], [], timeout)
        if not ready:
            return None
        line = self.proc.stdout.readline()
        if not line:
            raise ConnectionError("ACP process terminated")
        try:
            return json.loads(line.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None  # malformed line — skip

    def _wait_response(self, expected_id, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = max(0.1, deadline - time.monotonic())
            msg = self._readline(min(5, remaining))
            if not msg:
                continue
            if msg.get("id") == expected_id:
                if "error" in msg:
                    raise AcpError(f"RPC error: {msg['error']}")
                return msg.get("result")
            self._handle_agent_msg(msg)
        raise TimeoutError(f"No response for request {expected_id}")

    def _handle_agent_msg(self, msg):
        """Handle requests and notifications from the agent."""
        rid = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        if rid is not None and method:
            if method == "session/request_permission":
                options = params.get("options", [])
                allow = next(
                    (o for o in options if o["kind"] == "allow_all"),
                    next((o for o in options if o["kind"] == "allow"), options[0] if options else None),
                )
                opt_id = allow["optionId"] if allow else "allow"
                self._respond(rid, {"outcome": {"outcome": "selected", "optionId": opt_id}})
            elif method == "fs/read_text_file":
                path = params.get("path", "")
                try:
                    with open(path) as f:
                        self._respond(rid, {"content": f.read()})
                except Exception as e:
                    self._respond(rid, {"content": f"Error reading {path}: {e}"})
            elif method == "fs/write_text_file":
                path = params.get("path", "")
                content = params.get("content", "")
                try:
                    d = os.path.dirname(path)
                    if d:
                        os.makedirs(d, exist_ok=True)
                    with open(path, "w") as f:
                        f.write(content)
                    self._respond(rid, {})
                except Exception as e:
                    self._respond(rid, {"error": str(e)})
            else:
                self._respond(rid, {})

    # ── Lifecycle ─────────────────────────────────────────────────

    def _initialize(self):
        rid = self._send("initialize", {
            "protocolVersion": 1,
            "clientCapabilities": {
                "fs": {"readTextFile": True, "writeTextFile": True},
                "terminal": True,
            },
            "clientInfo": {"name": "autobuild", "version": "2.0.0"},
        })
        return self._wait_response(rid, timeout=15)

    def _new_session(self, cwd):
        rid = self._send("session/new", {"cwd": cwd, "mcpServers": []})
        result = self._wait_response(rid, timeout=15)
        self._session_id = result["sessionId"]
        return result

    def prompt(self, text: str, timeout: int = 600) -> str:
        """Send prompt and block until turn completes. Returns agent text."""
        rid = self._send("session/prompt", {
            "sessionId": self._session_id,
            "prompt": [{"type": "text", "text": text}],
        })

        chunks = []
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            remaining = max(0.1, deadline - time.monotonic())
            msg = self._readline(min(10, remaining))
            if not msg:
                continue

            if msg.get("id") == rid:
                if "error" in msg:
                    raise AcpError(f"Prompt error: {msg['error']}")
                return "".join(chunks)

            if msg.get("id") is not None and msg.get("method"):
                self._handle_agent_msg(msg)
                continue

            method = msg.get("method", "")
            if method == "session/update":
                update = msg.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if content.get("type") == "text":
                        chunks.append(content.get("text", ""))

        self.cancel()
        raise TimeoutError(f"Prompt timed out after {timeout}s")

    def cancel(self):
        try:
            self._send("session/cancel", {"sessionId": self._session_id}, is_request=False)
        except (BrokenPipeError, OSError):
            pass

    def close(self):
        """Kill the ACP subprocess and all its descendants."""
        descendants = self._get_descendants(self.proc.pid)
        for pid in descendants:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            self.proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            os.killpg(self.proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass

    @staticmethod
    def _get_descendants(pid):
        try:
            out = subprocess.check_output(["pgrep", "-P", str(pid)], text=True).strip()
            children = [int(p) for p in out.split() if p]
        except (subprocess.CalledProcessError, ValueError):
            return []
        result = list(children)
        for child in children:
            result.extend(AcpAgent._get_descendants(child))
        return result

    @property
    def alive(self):
        return self.proc.poll() is None


def run_wave(run_fn, items, max_workers=1, timeout=3600):
    """Run items in parallel via ThreadPoolExecutor. Returns list of (item, result|exception)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_item = {pool.submit(run_fn, item): item for item in items}
        try:
            for f in as_completed(future_to_item, timeout=timeout):
                item = future_to_item[f]
                try:
                    results.append((item, f.result()))
                except Exception as e:
                    results.append((item, e))
        except TimeoutError:
            log = _get_log()
            if log:
                log.error("Wave timeout — killing remaining agents")
        finally:
            _kill_orphan_acp_processes()
    return results


def _kill_orphan_acp_processes():
    """Kill any kiro-cli acp process trees spawned by this Python process."""
    pid = os.getpid()
    try:
        children = subprocess.check_output(
            ["pgrep", "-P", str(pid), "-f", "kiro-cli acp"], text=True
        ).strip().split()
        for cpid in children:
            try:
                os.killpg(int(cpid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                try:
                    os.kill(int(cpid), signal.SIGKILL)
                except (ProcessLookupError, OSError):
                    pass
    except subprocess.CalledProcessError:
        pass  # no children found
