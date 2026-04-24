---
name: tuimm-logd-reference
description: |
  logd — local log daemon and client library at ~/.kiro/tools/logd/.
  Use when: sending structured logs from Python scripts, querying logs by uid/service/level,
  tailing background process output, debugging pipeline runs, correlating parent-child logs.
  Contains: daemon commands, loglib API, query examples, LOGD_UID correlation pattern.
---

# logd — Local Log Daemon

UDP log collector with SQLite storage. Base tool for the `~/.kiro` ecosystem.

## Location

```
~/.kiro/tools/logd/
  logd.py      # daemon + CLI
  loglib.py    # client library
  logs.db      # SQLite database (WAL mode)
```

## Daemon Commands

```bash
python3 ~/.kiro/tools/logd/logd.py start       # start daemon (background)
python3 ~/.kiro/tools/logd/logd.py stop        # stop daemon
python3 ~/.kiro/tools/logd/logd.py status      # running? entry count? DB size?
python3 ~/.kiro/tools/logd/logd.py run         # foreground (debug)
```

## Query Commands

```bash
# Tail recent logs
python3 ~/.kiro/tools/logd/logd.py tail [N]                    # last N entries (default 30)
python3 ~/.kiro/tools/logd/logd.py tail --uid XXX              # filter by run uid
python3 ~/.kiro/tools/logd/logd.py tail --service autobuild    # filter by service
python3 ~/.kiro/tools/logd/logd.py tail --level ERROR          # filter by level
python3 ~/.kiro/tools/logd/logd.py tail --last 2h              # last 2 hours
python3 ~/.kiro/tools/logd/logd.py tail --json                 # JSON output

# Search
python3 ~/.kiro/tools/logd/logd.py search "pattern"            # text search
python3 ~/.kiro/tools/logd/logd.py search "failed" --service bg --last 1h

# List runs
python3 ~/.kiro/tools/logd/logd.py runs                        # recent execution runs
python3 ~/.kiro/tools/logd/logd.py runs --last 7d              # last 7 days
```

## Client Library (loglib)

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))
from loglib import get_logger

log = get_logger("my-service")
log.info("started", count=10)
log.error("failed", {"error": str(e), "file": path})
log.warn("slow query", duration=3.2)
log.debug("details", data={"key": "value"})
```

### Auto-detected context

loglib auto-detects and attaches to every log entry:
- `path` — git root or cwd
- `service` — caller-provided name
- `agent` — kiro-cli agent name (from parent process)
- `pid` — process ID
- `branch` — current git branch

### LOGD_UID Correlation

When `LOGD_UID` env var is set, loglib uses it as the uid instead of generating a new one. This correlates logs across parent-child processes:

```python
# Parent (orchestrator)
log = get_logger("coordinator")
os.environ["LOGD_UID"] = log.uid  # pass to children

# Child (spawned script) — automatically uses parent's uid
child_log = get_logger("worker")  # uid comes from LOGD_UID env var
```

bg and autobuild set LOGD_UID automatically on all child processes.

### Manual correlation

```python
# Pass uid explicitly
parent_log = get_logger("parent")
child_log = get_logger("child", uid=parent_log.uid)
```

## Schema

```sql
CREATE TABLE logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT NOT NULL,        -- run identifier
  ts TEXT NOT NULL,         -- timestamp
  level TEXT NOT NULL,      -- INFO/WARN/ERROR/DEBUG
  msg TEXT NOT NULL,        -- log message
  path TEXT NOT NULL,       -- git root or cwd
  service TEXT NOT NULL,    -- service name
  agent TEXT,               -- kiro-cli agent name
  pid INTEGER,              -- process ID
  branch TEXT,              -- git branch
  data TEXT                 -- JSON extra data
);
```

## Configuration

- Port: `127.0.0.1:5514` (UDP)
- Retention: 30 days (override with `LOGD_RETENTION_DAYS` env var)
- Database: `~/.kiro/tools/logd/logs.db` (SQLite WAL mode)

## Dependencies

None. Python stdlib only.
