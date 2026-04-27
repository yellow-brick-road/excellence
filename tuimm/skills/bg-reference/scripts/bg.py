#!/usr/bin/env python3
"""bg — Background execution library for ~/.kiro.

Two modes:
  CLI mode:  setup_bg() at top of script → --bg/--status/--tail/--stop
  Lib mode:  launch_bg(), is_running(), get_status(), stop()

Usage (CLI):
    import sys, os
    sys.path.insert(0, os.path.expanduser("~/.kiro/skills/bg-reference/scripts"))
    from bg import setup_bg
    setup_bg()  # intercepts flags, exits if found

Usage (Library):
    from bg import launch_bg, is_running, get_status, stop
    uid = launch_bg("scripts/gather.py", args=["--source", "rss"])
    print(get_status(uid))  # "running" | "finished" | "failed" | "not_found"
"""

import os, random, shlex, signal, subprocess, sys, time
from pathlib import Path

# ── logd integration (optional) ─────────────────────────────────────────────

_log = None


def _get_log():
    global _log
    if _log is None:
        try:
            sys.path.insert(0, os.path.expanduser("~/.kiro/skills/logd-reference/scripts"))
            from loglib import get_logger
            _log = get_logger("bg")
        except Exception:
            _log = False  # logd not available
    return _log if _log else None


def _log_info(msg, **data):
    log = _get_log()
    if log:
        log.info(msg, **data)


def _log_error(msg, **data):
    log = _get_log()
    if log:
        log.error(msg, **data)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _detect_project() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=2,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def _temp_dir() -> Path:
    d = Path(_detect_project()) / ".kiro" / "temp"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _gen_uid() -> str:
    return f"{time.strftime('%Y%m%d-%H%M')}-{random.randint(0, 0xfff):03x}"


def _pid_path(uid: str) -> Path:
    return _temp_dir() / f"{uid}.pid"


def _rc_path(uid: str) -> Path:
    return _temp_dir() / f"{uid}.rc"


def _read_file(path: Path) -> str | None:
    try:
        return path.read_text().strip()
    except (FileNotFoundError, ValueError):
        return None


def _read_pid(path: Path) -> int | None:
    val = _read_file(path)
    return int(val) if val else None


def _read_rc(path: Path) -> int | None:
    val = _read_file(path)
    if val is None or val == "":
        return None
    try:
        return int(val)
    except ValueError:
        return None


def _alive(pid: int) -> bool:
    try:
        os.waitpid(pid, os.WNOHANG)  # reap zombie if we're parent
    except (ChildProcessError, OSError):
        pass  # not our child or already reaped
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _latest_uid() -> str | None:
    """Find most recent PID file in temp dir."""
    temp = _temp_dir()
    pids = sorted(temp.glob("*.pid"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pids[0].stem if pids else None

def _log_path(uid: str) -> Path:
    return _temp_dir() / f"{uid}.log"


def _logd_tail(uid: str, lines: int = 5) -> list[str]:
    """Query logd for recent entries with this uid."""
    try:
        logd = os.path.expanduser("~/.kiro/skills/logd-reference/scripts/logd.py")
        r = subprocess.run(
            [sys.executable, logd, "tail", "--uid", uid, str(lines)],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()
    except Exception:
        pass
    return []


# ── Core: stop logic ────────────────────────────────────────────────────────

def _stop_process(pid: int, uid: str):
    """SIGTERM → 15s poll → SIGKILL. Cleanup PID/RC files."""
    if _alive(pid):
        try:
            os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        else:
            for _ in range(30):
                time.sleep(0.5)
                if not _alive(pid):
                    break
            else:
                try:
                    os.killpg(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        _log_info(f"stopped {uid}", pid=pid)
    _pid_path(uid).unlink(missing_ok=True)
    _rc_path(uid).unlink(missing_ok=True)
    # Keep log file for forensics — cleaned up by user or next run


# ── CLI mode ─────────────────────────────────────────────────────────────────

def _cli_bg():
    """Fork to background with shell RC wrapper."""
    uid = _gen_uid()
    pf = _pid_path(uid)

    # Already-running guard: check latest
    latest = _latest_uid()
    if latest:
        old_pid = _read_pid(_pid_path(latest))
        if old_pid and _alive(old_pid):
            print(f"already running (uid={latest}, PID {old_pid}) — stop it first", file=sys.stderr)
            sys.exit(1)

    argv = [a for a in sys.argv if a != "--bg"]
    rc = _rc_path(uid)
    cmd = shlex.join([sys.executable] + argv) + f" ; echo $? > {shlex.quote(str(rc))}"

    env = os.environ.copy()
    env["LOGD_UID"] = uid

    log_file = _log_path(uid)
    with open(log_file, "a") as lf:
        proc = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=lf, stderr=subprocess.STDOUT,
            start_new_session=True, env=env,
        )
    pf.write_text(str(proc.pid))
    _log_info(f"started --bg", pid=proc.pid, uid=uid, cmd=shlex.join(argv))
    print(uid)


def _cli_status():
    """Show status of most recent background run."""
    uid = _latest_uid()
    if not uid:
        print("no background runs found", file=sys.stderr)
        sys.exit(1)

    pid = _read_pid(_pid_path(uid))
    rc = _read_rc(_rc_path(uid))

    if pid is None:
        state = "no pid file"
    elif _alive(pid):
        state = f"running (uid={uid}, PID {pid})"
    elif rc is not None and rc != 0:
        state = f"FAILED (uid={uid}, rc={rc})"
    elif rc is not None:
        state = f"finished (uid={uid})"
    else:
        state = f"terminated (uid={uid}, no exit code)"
        # Stale PID cleanup
        _pid_path(uid).unlink(missing_ok=True)

    print(state, file=sys.stderr)

    # Show recent output: logd first, fallback to log file
    lines = _logd_tail(uid)
    if not lines:
        log_file = _log_path(uid)
        if log_file.exists():
            try:
                with open(log_file) as f:
                    lines = f.readlines()[-5:]
                    lines = [l.rstrip() for l in lines]
            except Exception:
                pass
    if lines:
        print("", file=sys.stderr)
        for l in lines:
            print(f"  {l}", file=sys.stderr)


def _cli_tail():
    """Delegate to logd tail, fallback to log file."""
    uid = _latest_uid()
    if not uid:
        print("no background runs found", file=sys.stderr)
        sys.exit(1)
    # Try logd first, fallback to log file
    log_file = _log_path(uid)
    if log_file.exists():
        os.execvp("tail", ["tail", "-f", str(log_file)])
    logd = os.path.expanduser("~/.kiro/skills/logd-reference/scripts/logd.py")
    os.execvp(sys.executable, [sys.executable, logd, "tail", "--uid", uid, "50"])


def _cli_stop():
    """Stop most recent background run."""
    uid = _latest_uid()
    if not uid:
        print("no background runs found", file=sys.stderr)
        sys.exit(1)

    pid = _read_pid(_pid_path(uid))
    if pid is None:
        print("no pid file", file=sys.stderr)
        sys.exit(1)

    if not _alive(pid):
        print(f"not running (uid={uid}, PID {pid})", file=sys.stderr)
        _pid_path(uid).unlink(missing_ok=True)
        return

    print(f"stopping {uid} (PID {pid})...", file=sys.stderr)
    _stop_process(pid, uid)
    print("stopped", file=sys.stderr)


def setup_bg(exclude: set | None = None):
    """Check sys.argv for --bg/--status/--tail/--stop. Act and exit if found.
    Pass exclude={'--status'} to handle specific flags yourself."""
    flags = {"--bg": _cli_bg, "--status": _cli_status, "--tail": _cli_tail, "--stop": _cli_stop}
    for flag, fn in flags.items():
        if flag in sys.argv and flag not in (exclude or set()):
            fn()
            sys.exit(0)


# ── Library mode ─────────────────────────────────────────────────────────────

def launch_bg(script: str, args: list[str] | None = None, env: dict | None = None) -> str:
    """Launch a script in background. Returns uid."""
    uid = _gen_uid()
    pf = _pid_path(uid)
    rc = _rc_path(uid)

    full_args = [sys.executable, script] + (args or [])
    cmd = shlex.join(full_args) + f" ; echo $? > {shlex.quote(str(rc))}"

    child_env = os.environ.copy()
    child_env["LOGD_UID"] = uid
    if env:
        child_env.update(env)

    log_file = _log_path(uid)
    with open(log_file, "a") as lf:
        proc = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=lf, stderr=subprocess.STDOUT,
            start_new_session=True, env=child_env,
        )
    pf.write_text(str(proc.pid))
    _log_info(f"started {script}", pid=proc.pid, uid=uid, args=args or [])
    return uid


def is_running(uid: str) -> bool:
    """Check if a background process is alive."""
    pid = _read_pid(_pid_path(uid))
    return pid is not None and _alive(pid)


def get_status(uid: str) -> str:
    """Returns 'running', 'finished', 'failed', or 'not_found'."""
    pf = _pid_path(uid)
    pid = _read_pid(pf)
    if pid is None:
        return "not_found"
    if _alive(pid):
        return "running"
    # Process is dead — wait briefly for shell wrapper to write RC file
    rc = _read_rc(_rc_path(uid))
    if rc is None:
        time.sleep(0.5)  # shell wrapper may still be writing
        rc = _read_rc(_rc_path(uid))
    if rc is not None and rc == 0:
        return "finished"
    if rc is not None:
        return "failed"
    # Still no RC after wait = crash/SIGKILL
    pf.unlink(missing_ok=True)
    return "failed"


def stop(uid: str):
    """Stop a background process by uid."""
    pid = _read_pid(_pid_path(uid))
    if pid is None:
        return
    _stop_process(pid, uid)


def get_log_tail(uid: str, lines: int = 5) -> list[str]:
    """Query logd for recent entries with this uid."""
    return _logd_tail(uid, lines)
