# ACP Integration — Internal Tooling Protocol Layer

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


How Agent Client Protocol (ACP) fits into the Excellence internal tooling stack.

## Context

ACP is a JSON-RPC 2.0 protocol over stdio for structured communication between clients and AI agents. Created by Zed Industries + JetBrains. Kiro CLI implements it via `kiro-cli acp`.

**Scope:** Internal tooling only. Production user-facing features use Vercel AI SDK + direct LLM APIs (see DECISIONS.md #3). ACP is for developer tools, automation, and CI — where we want to leverage existing kiro-cli agent configs (steering, skills, MCP servers) without managing API keys separately.

## Problem

Current tooling (`autobuild`, future `bot service`, `tui cli`) talks to kiro-cli via subprocess:

```
engine.py → subprocess("kiro-cli chat --no-interactive ...") → text output
```

This is:
- **Lossy** — output is text with ANSI codes, needs stripping and parsing
- **Opaque** — no visibility into what the agent does during execution
- **Expensive** — one process per call (3-25 per task in autobuild)
- **Uncontrolled** — no way to restrict what tools the agent uses
- **Brittle** — cancellation via SIGTERM, no graceful shutdown

## Solution

Replace subprocess calls with a persistent ACP connection:

```
engine.py → ACP (JSON-RPC over stdio) → kiro-cli acp → structured events
```

Single process, structured I/O, real-time streaming, permission control.

## Protocol Basics

```
Client (Python)                    Agent (kiro-cli acp)
  │                                    │
  │── initialize ─────────────────────>│  Capabilities exchange
  │── session/new ────────────────────>│  Create session with cwd
  │── session/prompt ─────────────────>│  Send task prompt
  │<── session/update (streaming) ─────│  Text chunks, tool calls, results
  │<── request_permission ─────────────│  "Can I write file X?"
  │── permission response ────────────>│  Allow/deny based on role
  │<── prompt result (end_turn) ───────│  Turn complete
  │── session/set_mode ───────────────>│  Switch agent for next phase
  │── session/cancel ─────────────────>│  Graceful cancellation
```

Transport: newline-delimited JSON over stdin/stdout. Python stdlib only (`json`, `subprocess`).

## What ACP Gives Us

### 1. Structured tool tracking

Every tool invocation arrives as typed JSON:

```json
{"sessionUpdate": "tool_call", "toolCallId": "call_001", "title": "Write file", "kind": "file_write", "status": "running"}
{"sessionUpdate": "tool_call_update", "toolCallId": "call_001", "status": "completed", "content": [...]}
```

Kinds: `file_read`, `file_write`, `terminal`, `other`. No text parsing needed. Direct feed to logd.

### 2. Permission control per role

The `requestPermission` callback lets the client decide what each role can do:

| Role | fs.read | fs.write | terminal | Use case |
|------|---------|----------|----------|----------|
| Builder | ✅ | ✅ | ✅ | Implements code |
| Reviewer | ✅ | ❌ | ❌ | Reviews only, can't modify |
| Architect | ✅ | ❌ | ❌ | Design review only |
| QA | ✅ | ❌ | ✅ | Reads code + runs verify commands |

Enforced at protocol level — the agent literally cannot write files if the client denies permission.

### 3. Single process, multiple sessions

Spawn `kiro-cli acp` once per pipeline run. Create sessions per task or reuse for context accumulation. No subprocess overhead per phase.

### 4. Real-time streaming

`agent_message_chunk` events arrive as the agent thinks. Feed directly to logd for live `--tail` output instead of waiting for subprocess completion.

### 5. Agent switching without respawn

`session/set_mode` changes the active agent config mid-session. In autobuild's `extended`/`full` modes, switch between Builder and Reviewer roles without spawning new processes.

### 6. Session forking

`unstable_forkSession` creates independent session copies sharing the same history. In autobuild `full` mode, fork once per candidate builder — each generates a plan from the same context without interference.

### 7. Graceful cancellation

`session/cancel` (notification) → agent finishes current operation and returns `stopReason: "cancelled"`. Clean state, no orphaned processes.

### 8. File system interception

The client implements `fs/read_text_file` and `fs/write_text_file`. This means the client controls all file I/O:
- Log every file operation with path and content
- Sandbox writes to project directory only
- Create before/after snapshots per task
- Generate automatic diffs

## Python ACP Client

Minimal implementation — JSON-RPC over stdio, no external dependencies:

```python
class AcpConnection:
    def __init__(self, cwd, uid, agent=None, model=None):
        self.proc = subprocess.Popen(
            ["kiro-cli", "acp"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.uid = uid
        self._id = 0
        self._handlers = {}
        self._initialize(cwd)

    def _send(self, method, params, is_notification=False):
        self._id += 1
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        if not is_notification:
            msg["id"] = self._id
        self.proc.stdin.write(json.dumps(msg).encode() + b"\n")
        self.proc.stdin.flush()
        return None if is_notification else self._id

    def _recv(self):
        line = self.proc.stdout.readline()
        return json.loads(line) if line else None

    def prompt(self, session_id, text, on_update=None, permissions=None):
        # Send prompt, process streaming updates, return structured result
        ...

    def set_mode(self, session_id, mode_id):
        # Switch agent
        ...

    def cancel(self, session_id):
        # Graceful cancel (notification, no response)
        self._send("session/cancel", {"sessionId": session_id}, is_notification=True)

    def close(self):
        self.proc.terminate()
        self.proc.wait()
```

The full implementation handles the async read loop (reading notifications while waiting for responses), permission callbacks, and timeout management. But the wire protocol is trivial — it's just `json.dumps` + newline.

## Integration Points

### autobuild (ideas/tooling/TOOL_AUTOBUILD.md)

Primary consumer. ACP replaces the subprocess backend in `kiro.py`.

| Feature | Subprocess (v1) | ACP (v2) |
|---------|-----------------|----------|
| Process per call | 1 | 0 (shared connection) |
| Output format | Text + ANSI | Structured JSON |
| Tool visibility | None | Full (kind, status, content) |
| Permission control | None | Per-role enforcement |
| Streaming | None (wait for exit) | Real-time to logd |
| Cancellation | SIGTERM | `session/cancel` |
| Agent switching | New subprocess | `session/set_mode` |
| Session forking | N/A | `unstable_forkSession` |

Backend selected via `autobuild.json`:
```json
{ "backend": "acp" }
```

### Bot Service (ideas/ai/AUTONOMOUS_BOT_SERVICE.md)

Event-driven autonomous agent invocation. Currently designed around subprocess spawning per webhook event.

With ACP: maintain a pool of persistent connections. Incoming webhook → pick available connection → create session → prompt → stream results → close session. Connection stays alive for next event.

Gains:
- Lower latency (no spawn overhead per event)
- Structured audit trail (every tool call logged)
- Permission enforcement (bot agents get restricted permissions)

### TUI CLI (ideas/tooling/TUI_CLI.md)

`tui ai chat` could be a thin ACP client instead of wrapping `kiro-cli chat`. Benefits:
- Custom UI (progress bars, tool call display, permission prompts)
- Session management (list, resume, fork)
- Agent switching from CLI UI

Lower priority — `kiro-cli chat` already works well for interactive use.

### MCP Gateway testing

Spin up agents via ACP to validate MCP server integrations programmatically. Create session → prompt agent to use specific MCP tool → verify tool_call events → assert results.

## Relationship to DECISIONS.md #3

No conflict. The decision states:

> LLM API directo en producción (Vercel AI SDK + Anthropic/OpenAI). kiro-cli ACP solo para POC/demos.

This applies to **production user-facing features** (search, recommendations, chat widgets). For those, direct API access is correct — lower latency, no kiro-cli dependency in production infra.

ACP is for **internal developer tooling** where:
- It runs on developer machines or CI, not production
- It leverages existing agent configs (steering, skills, MCP servers) for free
- No API key management needed (kiro-cli handles auth)
- The structured protocol adds value (permissions, streaming, tool tracking)

**Production = Vercel AI SDK. Internal tooling = ACP.**

## Implementation Priority

| Component | Priority | Effort | Value |
|-----------|----------|--------|-------|
| autobuild ACP backend | High | Medium | Structured output, permissions, streaming |
| Bot Service ACP pool | Medium | Medium | Lower latency, audit trail |
| TUI CLI ACP client | Low | Low | Nice-to-have, kiro-cli chat works |
| MCP Gateway test harness | Low | Low | Useful but not blocking |

autobuild is the first consumer. Once `kiro.py` has a working ACP backend, the pattern is reusable for Bot Service and others.

## Open Questions

- [ ] `unstable_forkSession` — is it stable enough for production use in autobuild `full` mode? Need to test with kiro-cli
- [ ] Connection pooling for Bot Service — how many concurrent ACP connections can kiro-cli handle? Memory/CPU per connection?
- [ ] ACP protocol version stability — v1 is current, but how often do breaking changes happen?
- [x] stderr handling — kiro-cli acp logs to stderr. Route to logd or discard? → `stderr=subprocess.DEVNULL` in poc.newspaper implementation
- [ ] Auth token refresh — long-running ACP connections (overnight autobuild runs) may need token refresh. Does kiro-cli handle this transparently?

## Status

Working implementation at `~/showmethemoney/poc.newspaper/scripts/lib/acp.py`. All 7 pipeline scripts migrated from subprocess to ACP (V2-10 ✅ Done 2026-03-17). autobuild's `kiro.py` still uses subprocess — pending migration to ACP as default backend.
