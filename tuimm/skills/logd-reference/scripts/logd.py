#!/usr/bin/env python3
"""logd — Local log collector daemon for ~/.kiro.

Receives JSON logs via UDP, writes to SQLite (~/.kiro/skills/logd-reference/scripts/logs.db).

Usage:
  logd.py start                                    # start daemon (background)
  logd.py stop                                     # stop daemon
  logd.py status                                   # running? entry count? DB size?
  logd.py run                                      # foreground (debug)
  logd.py tail [--uid U] [--path P] [--service S] [--level L] [--last Nh] [N]
  logd.py search PATTERN [--path P] [--service S] [--level L] [--last Nh]
  logd.py runs [--path P] [--last Nh]
"""
import argparse, json, os, signal, socket, sqlite3, sys, time
from datetime import datetime
from pathlib import Path

LOGD_DIR = Path(__file__).resolve().parent
DB_PATH = LOGD_DIR / "logs.db"
PID_FILE = LOGD_DIR / ".logd.pid"
HOST = "127.0.0.1"
PORT = 5514
BUF_SIZE = 65535

SCHEMA = """\
CREATE TABLE IF NOT EXISTS logs (
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
  data TEXT
);
CREATE INDEX IF NOT EXISTS idx_uid ON logs(uid);
CREATE INDEX IF NOT EXISTS idx_path_service ON logs(path, service, ts);
CREATE INDEX IF NOT EXISTS idx_level_ts ON logs(level, ts);
"""


def _init_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH))
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    return db


def _retention(db: sqlite3.Connection):
    try:
        days = int(os.environ.get("LOGD_RETENTION_DAYS", "30"))
    except ValueError:
        days = 30
    db.execute("DELETE FROM logs WHERE ts < datetime('now', 'localtime', ? || ' days')", (f"-{days}",))
    db.commit()


# ── Daemon ───────────────────────────────────────────────────────────────────

def run_daemon(foreground: bool = False):
    db = _init_db()
    _retention(db)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)

    PID_FILE.write_text(str(os.getpid()))
    if foreground:
        print(f"logd listening on {HOST}:{PORT} (foreground)", file=sys.stderr)

    running = True

    def _stop(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    try:
        while running:
            try:
                raw, _ = sock.recvfrom(BUF_SIZE)
            except socket.timeout:
                continue
            try:
                m = json.loads(raw)
                ctx = m.get("ctx", {})
                data_val = m.get("data")
                ts = m.get("ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ts = ts.replace("T", " ")  # normalize for SQLite comparisons
                db.execute(
                    "INSERT INTO logs (uid,ts,level,msg,path,service,agent,pid,branch,data)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        m.get("uid", ""),
                        ts,
                        m.get("level", "INFO"),
                        m.get("msg", ""),
                        ctx.get("path", ""),
                        ctx.get("service", ""),
                        ctx.get("agent"),
                        ctx.get("pid"),
                        ctx.get("branch"),
                        json.dumps(data_val, ensure_ascii=False) if data_val else None,
                    ),
                )
                db.commit()
                if foreground:
                    sys.stderr.write(
                        f"  {ctx.get('service','?')} [{m.get('level','?')}] {m.get('msg','')}\n"
                    )
            except Exception:
                pass  # malformed → drop
    finally:
        db.close()
        sock.close()
        PID_FILE.unlink(missing_ok=True)


# ── Process management ───────────────────────────────────────────────────────

def _get_pid() -> int | None:
    if not PID_FILE.exists():
        return None
    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        PID_FILE.unlink(missing_ok=True)
        return None


def cmd_start():
    if _get_pid():
        print("logd already running")
        return
    import subprocess
    subprocess.Popen(
        [sys.executable, __file__, "run"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(0.3)
    pid = _get_pid()
    print(f"logd started (PID {pid})" if pid else "logd failed to start")


def cmd_stop():
    pid = _get_pid()
    if not pid:
        print("logd not running")
        return
    os.kill(pid, signal.SIGTERM)
    print(f"logd stopped (PID {pid})")


def cmd_status():
    pid = _get_pid()
    if pid:
        if DB_PATH.exists():
            db = sqlite3.connect(str(DB_PATH))
            try:
                count = db.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
                size_mb = DB_PATH.stat().st_size / (1024 * 1024)
                print(f"logd running (PID {pid}), {count} entries, {size_mb:.1f} MB")
            finally:
                db.close()
        else:
            print(f"logd running (PID {pid}), no database yet")
    else:
        print("logd not running")


# ── Query helpers ────────────────────────────────────────────────────────────

def _parse_last(last: str | None) -> str | None:
    if not last:
        return None
    try:
        val, unit = int(last[:-1]), last[-1]
    except (ValueError, IndexError):
        return None
    if val <= 0:
        return None
    if unit == "h":
        return f"datetime('now', 'localtime', '-{val} hours')"
    if unit == "d":
        return f"datetime('now', 'localtime', '-{val} days')"
    return None


def _build_where(args) -> tuple[str, list]:
    clauses, params = [], []
    if getattr(args, "uid", None):
        clauses.append("uid = ?")
        params.append(args.uid)
    if getattr(args, "path", None):
        clauses.append("path LIKE ?")
        params.append(f"%{args.path}%")
    if getattr(args, "service", None):
        clauses.append("service = ?")
        params.append(args.service)
    if getattr(args, "level", None):
        clauses.append("level = ?")
        params.append(args.level.upper())
    ts_expr = _parse_last(getattr(args, "last", None))
    if ts_expr:
        clauses.append(f"ts >= {ts_expr}")
    return (" WHERE " + " AND ".join(clauses) if clauses else "", params)


_C = {"ERROR": "\033[31m", "WARN": "\033[33m", "DEBUG": "\033[90m", "INFO": "\033[36m"}
_R = "\033[0m"


def _fmt(row, as_json=False):
    ts, level, service, uid, msg, data = row
    if as_json:
        o = {"ts": ts, "level": level, "service": service, "uid": uid, "msg": msg}
        if data:
            o["data"] = json.loads(data)
        return json.dumps(o, ensure_ascii=False)
    c = _C.get(level, "")
    d = f"  {data}" if data else ""
    return f"{c}[{ts[11:]}] {level:<5}{_R} {service:<20} {msg}{d}"


def _open_db():
    if not DB_PATH.exists():
        print("No database yet")
        return None
    return sqlite3.connect(str(DB_PATH))


def cmd_tail(args):
    db = _open_db()
    if not db:
        return
    w, p = _build_where(args)
    rows = db.execute(
        f"SELECT ts,level,service,uid,msg,data FROM logs{w} ORDER BY id DESC LIMIT ?",
        p + [args.n or 30],
    ).fetchall()
    db.close()
    for r in reversed(rows):
        print(_fmt(r, getattr(args, "json", False)))


def cmd_search(args):
    db = _open_db()
    if not db:
        return
    w, p = _build_where(args)
    like = "msg LIKE ?"
    w = f"{w} AND {like}" if w else f" WHERE {like}"
    p.append(f"%{args.pattern}%")
    rows = db.execute(
        f"SELECT ts,level,service,uid,msg,data FROM logs{w} ORDER BY id DESC LIMIT 100", p
    ).fetchall()
    db.close()
    for r in reversed(rows):
        print(_fmt(r, getattr(args, "json", False)))


def cmd_runs(args):
    db = _open_db()
    if not db:
        return
    w, p = _build_where(args)
    rows = db.execute(
        f"SELECT uid, service, MIN(ts), COUNT(*) FROM logs{w}"
        " GROUP BY uid, service ORDER BY MIN(ts) DESC LIMIT 50",
        p,
    ).fetchall()
    db.close()
    if not rows:
        print("No runs found")
        return
    for uid, svc, started, cnt in rows:
        print(f"{started[5:16]}  {svc:<20} {uid}  ({cnt} entries)")


# ── Main ─────────────────────────────────────────────────────────────────────

def _add_filters(sp, with_uid=True):
    if with_uid:
        sp.add_argument("--uid", help="Filter by run UID")
    sp.add_argument("--path", help="Filter by path (substring)")
    sp.add_argument("--service", help="Filter by service")
    sp.add_argument("--level", help="Filter by level")
    sp.add_argument("--last", help="Time window (e.g. 2h, 7d)")
    sp.add_argument("--json", action="store_true", help="JSON output")


def main():
    p = argparse.ArgumentParser(description="Local log collector daemon")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("start", help="Start daemon")
    sub.add_parser("stop", help="Stop daemon")
    sub.add_parser("status", help="Check status")
    sub.add_parser("run", help="Run in foreground")

    t = sub.add_parser("tail", help="Tail logs")
    _add_filters(t)
    t.add_argument("n", nargs="?", type=int, default=30, help="Lines (default 30)")

    s = sub.add_parser("search", help="Search logs")
    s.add_argument("pattern", help="Search pattern (substring)")
    _add_filters(s)

    r = sub.add_parser("runs", help="List execution runs")
    _add_filters(r, with_uid=False)

    args = p.parse_args()
    cmds = {
        "start": cmd_start, "stop": cmd_stop, "status": cmd_status,
        "run": lambda: run_daemon(foreground=True),
        "tail": lambda: cmd_tail(args), "search": lambda: cmd_search(args),
        "runs": lambda: cmd_runs(args),
    }
    cmds.get(args.cmd, p.print_help)()


if __name__ == "__main__":
    main()
