"""loglib — Fire-and-forget UDP log client for ~/.kiro/tuimm/tools/logd.

Usage:
    import sys, os
    sys.path.insert(0, os.path.expanduser("~/.kiro/tuimm/tools/logd"))
    from loglib import get_logger

    log = get_logger("gather")
    log.info("fetched items", count=120, source="rss")
    log.error("boom", {"error": str(e)})

    # Cross-service correlation
    child_log = get_logger("classify", uid=log.uid)
"""
import json, os, random, socket, subprocess, time

LOGD_HOST = "127.0.0.1"
LOGD_PORT = 5514
_sock = None


def _get_sock() -> socket.socket:
    global _sock
    if _sock is None:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return _sock


def _gen_uid() -> str:
    return f"{time.strftime('%Y%m%d-%H%M')}-{random.randint(0,0xfff):03x}"


def _run(cmd: list[str]) -> str | None:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def _detect_path() -> str:
    return _run(["git", "rev-parse", "--show-toplevel"]) or os.getcwd()


def _detect_branch() -> str | None:
    return _run(["git", "branch", "--show-current"])


def _detect_agent() -> str | None:
    try:
        args = _run(["ps", "-p", str(os.getppid()), "-o", "args="])
        if args and "kiro-cli" in args:
            parts = args.split()
            for i, p in enumerate(parts):
                if p in ("--agent", "-a") and i + 1 < len(parts):
                    return parts[i + 1]
            return "kiro"
    except Exception:
        pass
    return None


class Logger:
    def __init__(self, service: str, uid: str | None = None):
        self.service = service
        self.uid = uid or os.environ.get("LOGD_UID") or _gen_uid()
        self._ctx = {
            "path": _detect_path(),
            "service": service,
            "agent": _detect_agent(),
            "pid": os.getpid(),
            "branch": _detect_branch(),
        }

    def _send(self, level: str, msg: str, data=None, **tags):
        merged = {}
        if isinstance(data, dict):
            merged.update(data)
        if tags:
            merged.update(tags)
        try:
            _get_sock().sendto(json.dumps({
                "uid": self.uid,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "level": level,
                "msg": msg,
                "ctx": self._ctx,
                "data": merged or None,
            }, ensure_ascii=False).encode(), (LOGD_HOST, LOGD_PORT))
        except Exception:
            pass

    def debug(self, msg: str, data=None, **tags): self._send("DEBUG", msg, data, **tags)
    def info(self, msg: str, data=None, **tags): self._send("INFO", msg, data, **tags)
    def warn(self, msg: str, data=None, **tags): self._send("WARN", msg, data, **tags)
    def error(self, msg: str, data=None, **tags): self._send("ERROR", msg, data, **tags)


def get_logger(service: str, uid: str | None = None) -> Logger:
    return Logger(service, uid)
