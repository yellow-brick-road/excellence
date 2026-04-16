# Tool: logd

Local log collector daemon for the `~/.kiro` ecosystem.

## What it is

A lightweight UDP log daemon that receives JSON messages and stores them in SQLite. Any Python script can send logs with zero config — fire-and-forget over UDP, no connection management, no blocking.

Two components:
- `logd.py` — daemon that listens on UDP 5514, writes to SQLite
- `loglib.py` — client library (single import, auto-detects context)

## Dependencies

None. Python stdlib only (`sqlite3`, `socket`, `json`, `subprocess`).

This is the base tool — everything else depends on it.

## Install path

```
~/.kiro/tools/logd/
  logd.py       # daemon
  loglib.py     # client library
  logs.db       # SQLite database (created at runtime)
```

## Log entry structure

Every log entry has three blocks:

```json
{
  "uid": "20260313-1244-a3f",
  "ts": "2026-03-13T12:44:51",
  "level": "INFO",
  "msg": "fetched 120 items",
  "ctx": {
    "path": "/home/user/showmethemoney/poc.newspaper",
    "service": "gather",
    "agent": "tars",
    "pid": 19229,
    "branch": "main"
  },
  "data": {
    "count": 120,
    "source": "rss"
  }
}
```

| Block | Purpose | Set by |
|-------|---------|--------|
| `uid` + `ts` + `level` + `msg` | What happened and when | Auto (uid at logger creation, ts per call) |
| `ctx` | Who is logging — immutable per execution | Auto-detected at `get_logger()` |
| `data` | Contextual payload for this specific call | Caller (optional, per call) |

### uid

Unique run identifier. Format: `YYYYMMDD-HHmm-xxx` (timestamp + 3-char random hex).
Generated once at `get_logger()` creation. All logs from the same logger share the same uid.
Orchestrators can pass their uid to child scripts for cross-service correlation.

### ctx fields (auto-detected)

| Field | Source | Description |
|-------|--------|-------------|
| `path` | `git rev-parse --show-toplevel` or `os.getcwd()` | Absolute path to project root |
| `service` | Caller (required) | Script/component name ("gather", "classify") |
| `agent` | `ps -p $PPID -o args=` | Kiro agent name if parent is kiro-cli, else `null` |
| `pid` | `os.getpid()` | Process ID |
| `branch` | `git branch --show-current` | Current git branch, else `null` |

### data (optional)

Arbitrary dict passed per log call. Use for:
- Error details: `{"error": str(e), "traceback": tb}`
- Metrics: `{"elapsed_ms": 4500, "items": 120}`
- Context snapshots: `{"url": url, "status_code": 500}`

## Client API (loglib.py)

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))
from loglib import get_logger

# Basic — everything auto-detected
log = get_logger("gather")

# With explicit uid (for correlation with parent orchestrator)
log = get_logger("classify", uid=parent_log.uid)

# Logging
log.info("fetched items", {"count": 120, "source": "rss"})
log.error("connection failed", {"error": str(e), "url": url})
log.warn("slow response", {"elapsed_ms": 4500})
log.debug("raw payload", {"payload": raw})

# Access uid for passing to child processes
print(log.uid)  # "20260313-1244-a3f"
```

- Fire-and-forget UDP — if daemon is down, messages are silently dropped
- No dependencies beyond Python stdlib
- `data` is optional on every call — pass `None` or omit

## Wire protocol

UDP datagram to `127.0.0.1:5514`, JSON-encoded:

```json
{
  "uid": "20260313-1244-a3f",
  "ts": "2026-03-13T12:44:51",
  "level": "INFO",
  "msg": "fetched 120 items",
  "ctx": {
    "path": "/home/user/showmethemoney/poc.newspaper",
    "service": "gather",
    "agent": "tars",
    "pid": 19229,
    "branch": "main"
  },
  "data": { "count": 120, "source": "rss" }
}
```

Required: `uid`, `ts`, `level`, `msg`, `ctx` (with at least `path` and `service`).
Optional: `ctx.agent`, `ctx.branch`, `data`.

## Storage: SQLite

Single database at `~/.kiro/tools/logd/logs.db`.

```sql
CREATE TABLE logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL,
  ts TEXT NOT NULL,
  level TEXT NOT NULL,
  msg TEXT NOT NULL,
  path TEXT NOT NULL,
  service TEXT NOT NULL,
  agent TEXT,
  pid INTEGER,
  branch TEXT,
  data TEXT              -- JSON string, nullable
);

CREATE INDEX idx_uid ON logs(uid);
CREATE INDEX idx_path_service ON logs(path, service, ts);
CREATE INDEX idx_level_ts ON logs(level, ts);
```

WAL mode enabled for concurrent reads/writes.

### Retention

On daemon start, delete entries older than 30 days:
```sql
DELETE FROM logs WHERE ts < datetime('now', '-30 days');
```

Configurable via `LOGD_RETENTION_DAYS` env var (default: 30).

## Daemon CLI (logd.py)

```bash
logd.py start                                    # start daemon (background)
logd.py stop                                     # stop daemon (SIGTERM)
logd.py status                                   # running? PID? entry count? DB size?
logd.py run                                      # foreground mode (debug)

logd.py tail [--uid UID] [--path P] [--service S] [--level L] [--last Nh] [N]
logd.py search PATTERN [--path P] [--service S] [--level L] [--last Nh]
logd.py runs [--path P] [--last Nh]              # list recent execution runs
```

Examples:
```bash
logd.py tail --path "*/poc.newspaper" --service gather 50
logd.py tail --uid 20260313-1244-a3f
logd.py tail --level ERROR --last 2h
logd.py search "timeout" --path "*/poc.newspaper"
logd.py search "failed" --level ERROR --last 24h
logd.py runs --path "*/poc.newspaper" --last 7d
logd.py runs --last 1h                           # what ran in the last hour
```

### Output format

Default: human-readable colored output.
`--json` flag: JSON lines for programmatic consumption.

## Daemon internals

- PID file: `~/.kiro/tools/logd/.logd.pid`
- Graceful shutdown on SIGTERM/SIGINT (closes DB connection)
- Max datagram size: 64KB
- Malformed messages silently dropped
- SQLite WAL mode for non-blocking reads during writes
- Retention cleanup on startup

## Startup

Started by `tui cli setup` or manually. Auto-start not implemented — if daemon is down, logs are silently dropped (fire-and-forget contract).

## Requirements

- Python 3.10+
- No pip dependencies (stdlib only: `sqlite3`, `socket`, `json`, `subprocess`, `os`)

## Registry manifest

```json
{
  "name": "logd",
  "version": "2.0.0",
  "deps": [],
  "install_path": "~/.kiro/tools/logd",
  "files": ["logd.py", "loglib.py"],
  "requires": { "python": ">=3.10" }
}
```
