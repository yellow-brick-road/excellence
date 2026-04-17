#!/usr/bin/env python3
"""gitlab-list-mrs.py — Cross-repo MR listing for TUIMM agents.

Usage: python3 gitlab-list-mrs.py [username]

Returns JSON array of MRs with: iid, title, author, project_path, repo_name,
roles, is_bot, draft, has_conflicts, merge_status, pipeline, approvals,
approved_by, approvals_left, days_open, created_at, updated_at

Strategy (fast, no config):
  1. Own MRs: 3 global queries (reviewer, assignee, author) — server-side
  2. Bot MRs: from step 1, extract active project_ids → check only those for bot MRs
  3. Approvals: 1 query per non-draft MR

Environment:
  GITLAB_PERSONAL_ACCESS_TOKEN  (required)
  GITLAB_API_URL                (optional, default: https://source.tui/api/v4)
"""

import json
import os
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

TOKEN = os.environ.get("GITLAB_PERSONAL_ACCESS_TOKEN")
if not TOKEN:
    print("ERROR: GITLAB_PERSONAL_ACCESS_TOKEN not set. See SETUP.md", file=sys.stderr)
    sys.exit(1)

API = os.environ.get("GITLAB_API_URL", "https://source.tui/api/v4").rstrip("/")

if len(sys.argv) > 1:
    USERNAME = sys.argv[1]
else:
    try:
        USERNAME = subprocess.check_output(
            ["git", "config", "--global", "user.email"], stderr=subprocess.DEVNULL, timeout=5
        ).decode().strip().split("@")[0]
    except Exception:
        print("ERROR: No username provided and git config user.email not set", file=sys.stderr)
        sys.exit(1)

BOT_KEYWORDS = ["bot", "renovate", "dependabot", "onesource", "snyk"]


def fetch(url: str) -> list | dict | None:
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "15", "-H", f"PRIVATE-TOKEN: {TOKEN}", url],
            capture_output=True, text=True
        )
        return json.loads(r.stdout) if r.stdout.strip() else []
    except (json.JSONDecodeError, Exception):
        return []


def is_bot(author: str) -> bool:
    a = author.lower()
    return any(k in a for k in BOT_KEYWORDS)


def make_entry(mr: dict, roles: list, project_path: str = "") -> dict:
    author = mr.get("author", {}).get("username", "?")
    pp = project_path or mr.get("references", {}).get("full", "").rsplit("!", 1)[0].strip()
    return {
        "id": mr["id"],
        "iid": mr["iid"],
        "title": mr["title"],
        "author": author,
        "assignees": [a["username"] for a in mr.get("assignees", [])],
        "reviewers": [r["username"] for r in mr.get("reviewers", [])],
        "draft": mr.get("draft", False),
        "has_conflicts": mr.get("has_conflicts", False),
        "merge_status": mr.get("detailed_merge_status", mr.get("merge_status", "unknown")),
        "target_branch": mr.get("target_branch", ""),
        "source_branch": mr.get("source_branch", ""),
        "created_at": mr["created_at"][:10],
        "created_at_full": mr["created_at"],
        "updated_at": mr["updated_at"][:16],
        "pipeline": (mr.get("head_pipeline") or {}).get("status", "none"),
        "web_url": mr.get("web_url", ""),
        "project_id": mr.get("project_id"),
        "project_path": pp,
        "roles": roles,
        "is_bot": is_bot(author),
    }


# --- 1-3: Own MRs (reviewer + assignee + author) ---

seen: dict[int, dict] = {}
all_mrs: list[dict] = []

for role, param in [
    ("reviewer", "reviewer_username"),
    ("assignee", "assignee_username"),
    ("author", "author_username"),
]:
    mrs = fetch(f"{API}/merge_requests?scope=all&state=opened&{param}={USERNAME}&per_page=100")
    if not isinstance(mrs, list):
        continue
    for mr in mrs:
        mid = mr["id"]
        if mid in seen:
            seen[mid]["roles"].append(role)
            continue
        entry = make_entry(mr, [role])
        seen[mid] = entry
        all_mrs.append(entry)

own_ids = set(seen.keys())

# --- 4: Bot MRs from user's active projects ---
# Active = projects from own open MRs + projects with recent merged MRs by user

active_projects: dict[int, str] = {}
for mr in all_mrs:
    pid = mr.get("project_id")
    pp = mr.get("project_path", "")
    if pid and pp:
        active_projects[pid] = pp

# Discover more projects from recently merged MRs (last 30 days)
from datetime import timedelta
cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
for role, param in [("author", "author_username"), ("reviewer", "reviewer_username")]:
    merged = fetch(
        f"{API}/merge_requests?scope=all&state=merged&{param}={USERNAME}"
        f"&updated_after={cutoff}&per_page=100&view=simple"
    )
    if isinstance(merged, list):
        for mr in merged:
            pid = mr.get("project_id")
            if pid and pid not in active_projects:
                pp = mr.get("references", {}).get("full", "").rsplit("!", 1)[0].strip()
                if pp:
                    active_projects[pid] = pp

for pid, path in active_projects.items():
    encoded = urllib.parse.quote(path, safe="")
    mrs = fetch(f"{API}/projects/{encoded}/merge_requests?state=opened&per_page=50")
    if not isinstance(mrs, list):
        continue
    for mr in mrs:
        if mr["id"] in seen:
            continue
        author = mr.get("author", {}).get("username", "?")
        if not is_bot(author):
            continue
        entry = make_entry(mr, ["bot_unassigned"], path)
        seen[mr["id"]] = entry
        all_mrs.append(entry)

# --- 5: Approvals + days_open ---

now = datetime.now(timezone.utc)

for mr in all_mrs:
    try:
        created = datetime.fromisoformat(mr["created_at_full"])
        mr["days_open"] = (now - created).days
    except Exception:
        mr["days_open"] = 0

    mr["repo_name"] = mr["project_path"].rsplit("/", 1)[-1] if mr["project_path"] else "?"

    if mr["draft"]:
        mr["approvals"] = 0
        mr["approved_by"] = []
        mr["approvals_left"] = "?"
        continue

    proj = mr.get("project_path", "")
    if not proj:
        mr["approvals"] = "?"
        mr["approved_by"] = []
        mr["approvals_left"] = "?"
        continue

    encoded = urllib.parse.quote(proj, safe="")
    try:
        data = fetch(f"{API}/projects/{encoded}/merge_requests/{mr['iid']}/approvals")
        if isinstance(data, dict):
            mr["approvals"] = len(data.get("approved_by", []))
            mr["approved_by"] = [a["user"]["username"] for a in data.get("approved_by", [])]
            mr["approvals_left"] = data.get("approvals_left", "?")
        else:
            mr["approvals"] = "?"
            mr["approved_by"] = []
            mr["approvals_left"] = "?"
    except Exception:
        mr["approvals"] = "?"
        mr["approved_by"] = []
        mr["approvals_left"] = "?"

for mr in all_mrs:
    mr.pop("created_at_full", None)

json.dump(all_mrs, sys.stdout, indent=2)
