---
name: bg-reference
description: |
  bg — background execution library at ~/.kiro/tuimm/tools/bg/.
  Use when: running scripts in background, checking process status, stopping background tasks,
  building orchestrators that launch/monitor child scripts, integrating --bg/--status/--stop into any script.
  Contains: setup_bg() API, launch_bg() API, status/stop/tail commands, LOGD_UID propagation.
---

# bg — Background Execution Library

Gives any Python script background execution capabilities. Two modes: CLI (flags) and Library (programmatic).

## Location

```
~/.kiro/tuimm/tools/bg/bg.py
```

## CLI Mode — setup_bg()

Add to the top of any script to get --bg/--status/--tail/--stop flags:

```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.kiro/tuimm/tools/bg"))
from bg import setup_bg

setup_bg()  # intercepts flags, exits if found
# ... rest of script runs normally if no flag
```

```bash
python3 my-script.py --bg       # fork to background, print uid
python3 my-script.py --status   # running? finished? failed?
python3 my-script.py --tail     # tail log file (live)
python3 my-script.py --stop     # SIGTERM → 15s → SIGKILL
```

### Exclude flags

If your script handles --status itself (e.g., autobuild's rich progress table):

```python
setup_bg(exclude={"--status"})  # bg won't intercept --status
```

### What --bg does

1. Already-running guard (refuses if process alive)
2. Generates uid (`YYYYMMDD-HHmm-xxx`)
3. Forks via shell wrapper: `python3 script.py ; echo $? > {uid}.rc`
4. Sets `LOGD_UID` env var on child
5. Redirects stdout/stderr to `{project}/.kiro/temp/{uid}.log`
6. Writes PID file
7. Prints uid to stdout

### What --status shows

```
running (uid=20260325-1400-a3f, PID 12345)

  [10:00] INFO  autobuild  starting task 01_setup
  [10:01] INFO  autobuild  task 01_setup passed
```

Shows state (running/finished/FAILED/terminated) + last 5 lines from log file or logd.

### What --stop does

SIGTERM to process group → poll 15s every 0.5s → SIGKILL if still alive → cleanup PID/RC files. Log file kept for forensics.

## Library Mode

For orchestrators that launch and monitor child scripts:

```python
from bg import launch_bg, is_running, get_status, stop, get_log_tail

# Launch
uid = launch_bg("scripts/gather.py", args=["--source", "rss"], env={"KEY": "val"})

# Monitor
is_running(uid)      # True/False
get_status(uid)      # "running" | "finished" | "failed" | "not_found"
get_log_tail(uid, 5) # last 5 logd entries

# Stop
stop(uid)
```

`launch_bg` sets LOGD_UID automatically — child logs correlate with parent.

## Artifacts

```
{project}/.kiro/temp/
  {uid}.pid    # PID (plain text)
  {uid}.rc     # exit code (written by shell wrapper — crash-safe)
  {uid}.log    # stdout/stderr capture
```

- RC file is written by bash, not Python — survives crashes/SIGKILL
- Log file persists after --stop for forensics
- PID file cleaned up on --stop or stale detection

## Dependencies

- logd (`~/.kiro/tuimm/tools/logd/`) — for structured logging and LOGD_UID correlation
- Python 3.10+, stdlib only
