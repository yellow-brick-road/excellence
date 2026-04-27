#!/usr/bin/env python3
"""Helper script for obs_dd_scan logd integration.

Two actions:
  save           — log structured scan results to logd
  load-previous  — retrieve the most recent scan for a service

Usage:
  python3 obs_scan.py save '<json>'
  python3 obs_scan.py load-previous --service <name>
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys

LOGD_DIR = os.path.expanduser("~/.kiro/skills/logd-reference/scripts")
LOGD_DB = os.path.join(LOGD_DIR, "logs.db")
LOGD_PY = os.path.join(LOGD_DIR, "logd.py")

sys.path.insert(0, LOGD_DIR)


def ensure_logd_running():
    """Start logd if not already running."""
    try:
        result = subprocess.run(
            [sys.executable, LOGD_PY, "status"],
            capture_output=True, text=True, timeout=5
        )
        if "running" not in result.stdout.lower():
            subprocess.run(
                [sys.executable, LOGD_PY, "start"],
                capture_output=True, text=True, timeout=5
            )
    except Exception:
        subprocess.run(
            [sys.executable, LOGD_PY, "start"],
            capture_output=True, text=True, timeout=5
        )


def cmd_save(data_json: str):
    """Log scan results to logd."""
    ensure_logd_running()
    from loglib import get_logger

    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"ok": False, "error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    log = get_logger("obs_dd_scan")

    log.info("scan_start", {
        "service": data.get("service", ""),
        "repo": data.get("repo", ""),
        "version": data.get("version", ""),
        "window_from": data.get("window_from", ""),
        "window_to": data.get("window_to", ""),
    })

    for p in data.get("patterns", []):
        log.info("pattern", {
            "error": p.get("error", ""),
            "count": p.get("count", 0),
            "severity": p.get("severity", ""),
            "status": p.get("status", ""),
            "service": data.get("service", ""),
            "is_bot": p.get("is_bot", False),
            "first_seen": p.get("first_seen", ""),
            "last_seen": p.get("last_seen", ""),
        })

    summary = data.get("summary", {})
    log.info("scan_end", {
        "service": data.get("service", ""),
        "total_errors_users": summary.get("total_errors_users", 0),
        "total_errors_bots": summary.get("total_errors_bots", 0),
        "patterns_total": summary.get("patterns_total", 0),
        "critical": summary.get("critical", 0),
        "high": summary.get("high", 0),
        "medium": summary.get("medium", 0),
        "low": summary.get("low", 0),
        "new": summary.get("new", 0),
        "resolved": summary.get("resolved", 0),
        "spikes": summary.get("spikes", 0),
    })

    print(json.dumps({"ok": True, "uid": log.uid}))


def cmd_load_previous(service: str):
    """Find the most recent scan for a service from logd SQLite."""
    if not os.path.exists(LOGD_DB):
        print(json.dumps({"found": False}))
        return

    conn = sqlite3.connect(LOGD_DB)
    conn.row_factory = sqlite3.Row

    # Find most recent scan_end for this service
    row = conn.execute(
        """
        SELECT uid, ts, data FROM logs
        WHERE service = 'obs_dd_scan' AND msg = 'scan_end'
          AND data LIKE ?
        ORDER BY ts DESC LIMIT 1
        """,
        (f'%"service": "{service}"%',)
    ).fetchone()

    if not row:
        # Try without space after colon (json.dumps compact)
        row = conn.execute(
            """
            SELECT uid, ts, data FROM logs
            WHERE service = 'obs_dd_scan' AND msg = 'scan_end'
              AND data LIKE ?
            ORDER BY ts DESC LIMIT 1
            """,
            (f'%"service":"{service}"%',)
        ).fetchone()

    if not row:
        conn.close()
        print(json.dumps({"found": False}))
        return

    uid = row["uid"]
    scan_date = row["ts"]
    end_data = json.loads(row["data"]) if row["data"] else {}

    # Get all pattern entries with same uid
    patterns = []
    for p in conn.execute(
        "SELECT data FROM logs WHERE uid = ? AND msg = 'pattern' ORDER BY id",
        (uid,)
    ):
        if p["data"]:
            patterns.append(json.loads(p["data"]))

    conn.close()

    print(json.dumps({
        "found": True,
        "scan_date": scan_date,
        "patterns": patterns,
        "summary": {
            "total_errors_users": end_data.get("total_errors_users", 0),
            "total_errors_bots": end_data.get("total_errors_bots", 0),
        }
    }))


def main():
    parser = argparse.ArgumentParser(description="obs_dd_scan logd helper")
    sub = parser.add_subparsers(dest="action", required=True)

    save_p = sub.add_parser("save")
    save_p.add_argument("json_data", help="JSON string with scan results")

    load_p = sub.add_parser("load-previous")
    load_p.add_argument("--service", required=True, help="Datadog service name")

    args = parser.parse_args()

    if args.action == "save":
        cmd_save(args.json_data)
    elif args.action == "load-previous":
        cmd_load_previous(args.service)


if __name__ == "__main__":
    main()
