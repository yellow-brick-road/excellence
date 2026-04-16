# Tool: bg

Background execution helpers for Python scripts.

## What it is

A library that gives any Python script background execution capabilities: daemonize, PID tracking, status checks, stop, and log tailing via logd. Also provides a programmatic API for orchestrators to launch and monitor child scripts.

Two usage modes:
- **CLI mode** — `setup_bg()` at the top of any script gives it `--bg/--status/--tail/--stop` flags
- **Library mode** — `launch_bg()`, `is_running()`, `get_status()` for orchestrators managing child processes

## Dependencies

| Tool | Why |
|------|-----|
| logd | All logging goes through logd. Tail delegates to `logd.py tail --uid`. |

## Install path

```
~/.kiro/tools/bg/
  bg.py         # library + CLI flag handler
```

## CLI mode

Any script that calls `setup_bg()` at startup gets these flags:

```bash
python3 my-script.py --bg       # fork to background, print uid
python3 my-script.py --status   # running? finished? failed?
python3 my-script.py --tail     # tail logs via logd (by uid)
python3 my-script.py --stop     # SIGTERM the process
```

Usage:
```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
from bg import setup_bg

setup_bg()  # intercepts --bg/--status/--tail/--stop, exits if found
# ... rest of script runs normally if no flag present
```

`setup_bg()` checks `sys.argv` for flags. If found, it acts and calls `sys.exit(0)`. If no flag, returns and the script continues normally.

### How --bg works

1. **Guard**: checks if PID file exists and process is alive → refuses with "already running (PID N), stop it first"
2. Generates a uid (same format as logd: `YYYYMMDD-HHmm-xxx`)
3. Forks the process (`start_new_session=True`) via shell wrapper that captures exit code:
   ```bash
   python3 my-script.py ; echo $? > {rc_path}
   ```
4. Sets `LOGD_UID` env var on the child so logd auto-correlates
5. Writes PID file to `{project}/.kiro/temp/{uid}.pid`
6. Prints uid to stdout (parent captures it)
7. Parent exits, child continues running

### How --status works

1. Finds most recent PID file in `{project}/.kiro/temp/`
2. Checks if process is alive (`os.kill(pid, 0)`)
3. Checks return code file (`.rc`) to distinguish outcomes:
   - PID alive → `running (uid=XXX, pid=1234)`
   - PID dead + rc=0 → `finished (uid=XXX)`
   - PID dead + rc≠0 → `FAILED (uid=XXX, rc=N)`
   - PID dead + no rc → `terminated (uid=XXX, no exit code)` (crash/SIGKILL)
4. Queries logd for last N entries with that uid (default 5)
5. Prints state + recent log lines for quick debugging

### How --tail works

Delegates to `logd.py tail --uid XXX` using the uid from the most recent PID file.

### How --stop works

1. Reads PID from most recent PID file
2. Sends SIGTERM to process group (`os.killpg`) — "please stop gracefully"
3. Polls every 0.5s for up to 15 seconds, checking if process died
4. If still alive after timeout → sends SIGKILL ("no negotiation")
5. Cleanup: removes PID file and RC file

## Library mode

For orchestrators that launch and monitor child scripts programmatically:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
from bg import launch_bg, is_running, get_status

# Launch a script in background, returns uid
uid = launch_bg("scripts/gather.py", args=["--source", "rss"])

# Check if still running
if is_running(uid):
    print("still going")

# Get status
status = get_status(uid)  # "running" | "finished" | "failed" | "not_found"
```

### launch_bg(script, args=[], env={})

1. Generates uid
2. Sets `LOGD_UID={uid}` in child env (so child's logd entries correlate)
3. Spawns process with `start_new_session=True`
4. Writes PID file to `{project}/.kiro/temp/{uid}.pid`
5. Logs to logd: `"started {script}"` with data `{"pid": N, "args": [...]}`
6. Returns uid

### is_running(uid) → bool

Checks if PID file exists and process is alive.

### get_status(uid) → str

Returns `"running"`, `"finished"`, `"failed"`, or `"not_found"`.
Determines status by checking PID liveness and logd entries.

## Artifacts

PID and RC files, stored in the project directory:

```
{project}/.kiro/temp/{uid}.pid    # PID as plain text
{project}/.kiro/temp/{uid}.rc     # exit code as plain text (written by shell wrapper)
```

- PID file: created on launch, removed on --stop or cleanup
- RC file: written by the shell wrapper AFTER the process exits (`cmd ; echo $? > rc`). Survives crashes because the shell writes it, not Python
- All other state (logs, status, timing) lives in logd

### Why both logd and RC files?

logd gets the structured log when the process exits normally (the script logs "finished" before exiting). But if the process crashes hard (SIGKILL, OOM, segfault), it can't log anything — it's dead. The RC file is the crash-safe fallback: the shell wrapper always writes the exit code, regardless of how the process died. `get_status()` checks both: logd for details, RC for the definitive exit code.

## LOGD_UID correlation

When bg launches a process (via --bg or launch_bg), it sets `LOGD_UID` as an environment variable. loglib's `get_logger()` checks for this env var:

- If `LOGD_UID` is set → uses it as uid (correlation with parent)
- If not set → generates a new uid

This means child scripts don't need any special code. They just use `get_logger()` normally and their logs are automatically correlated with the bg execution.

## Process management

- Background processes run in their own session (`start_new_session=True`)
- `--stop` sends SIGTERM to the entire process group (`os.killpg`)
- Stale PID files (process dead but file remains) are detected and cleaned up on --status

## Requirements

- Python 3.10+
- No pip dependencies (stdlib only)
- logd installed (`~/.kiro/tools/logd/`)

## Registry manifest

```json
{
  "name": "bg",
  "version": "2.0.0",
  "deps": ["logd"],
  "install_path": "~/.kiro/tools/bg",
  "files": ["bg.py"],
  "requires": { "python": ">=3.10" }
}
```
