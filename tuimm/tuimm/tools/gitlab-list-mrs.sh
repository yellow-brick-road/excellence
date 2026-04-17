#!/usr/bin/env bash
# gitlab-list-mrs.sh — Cross-repo MR listing for TUIMM agents
# Usage: gitlab-list-mrs.sh [username]
#
# Returns JSON array of MRs with: iid, title, author, project_path, repo_name,
# roles, is_bot, draft, has_conflicts, merge_status, pipeline, approvals,
# approved_by, approvals_left, days_open, created_at, updated_at
#
# Queries:
#   1. MRs where user is reviewer (cross-project)
#   2. MRs where user is assignee (cross-project)
#   3. MRs where user is author (cross-project)
#   4. Unassigned bot MRs from user's projects (auto-discovered via API)
#   5. Approvals for all non-draft MRs
#
# Environment:
#   GITLAB_PERSONAL_ACCESS_TOKEN  (required) — from SETUP.md
#   GITLAB_API_URL                (optional) — defaults to https://source.tui/api/v4

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Config ---

TOKEN="${GITLAB_PERSONAL_ACCESS_TOKEN:?ERROR: GITLAB_PERSONAL_ACCESS_TOKEN not set. See SETUP.md}"
API="${GITLAB_API_URL:-https://source.tui/api/v4}"

# Username: argument > git config > error
if [ -n "${1:-}" ]; then
  USERNAME="$1"
else
  USERNAME=$(git config --global user.email 2>/dev/null | sed 's/@.*//' || true)
  if [ -z "$USERNAME" ]; then
    echo "ERROR: No username provided and git config user.email not set" >&2
    exit 1
  fi
fi

# --- Fetch user's own MRs (reviewer + assignee + author) ---

OWN_MRS=$(_API="$API" _TOKEN="$TOKEN" _USERNAME="$USERNAME" python3 << 'PYEOF'
import json, sys, subprocess, os

api = os.environ["_API"]
token = os.environ["_TOKEN"]
username = os.environ["_USERNAME"]

def fetch(url):
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "15", "-H", f"PRIVATE-TOKEN: {token}", url],
        capture_output=True, text=True
    )
    try:
        return json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError:
        return []

bot_keywords = ["bot", "renovate", "dependabot", "onesource", "snyk"]

def is_bot_author(name):
    a = name.lower()
    return any(k in a for k in bot_keywords)

seen = {}
results = []

for role, param in [
    ("reviewer", "reviewer_username"),
    ("assignee", "assignee_username"),
    ("author", "author_username"),
]:
    mrs = fetch(f"{api}/merge_requests?scope=all&state=opened&{param}={username}&per_page=100")
    if not isinstance(mrs, list):
        continue
    for mr in mrs:
        mid = mr["id"]
        if mid in seen:
            seen[mid]["roles"].append(role)
            continue
        author = mr.get("author", {}).get("username", "?")
        entry = {
            "id": mid,
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
            "project_path": mr.get("references", {}).get("full", "").rsplit("!", 1)[0].strip(),
            "roles": [role],
            "is_bot": is_bot_author(author),
        }
        seen[mid] = entry
        results.append(entry)

json.dump(results, sys.stdout)
PYEOF
)

# --- Fetch bot MRs from user's projects (auto-discovered) ---

BOT_MRS=$(_API="$API" _TOKEN="$TOKEN" _OWN_MRS="$OWN_MRS" _USERNAME="$USERNAME" python3 << 'PYEOF'
import json, sys, subprocess, urllib.parse, os

api = os.environ["_API"]
token = os.environ["_TOKEN"]
own_mrs_json = os.environ["_OWN_MRS"]
username = os.environ["_USERNAME"]

own_mrs = json.loads(own_mrs_json) if own_mrs_json else []
own_mrs_ids = {m["id"] for m in own_mrs}

bot_keywords = ["bot", "renovate", "dependabot", "onesource", "snyk"]

def is_bot(author):
    a = author.lower()
    return any(k in a for k in bot_keywords)

def fetch(url):
    r = subprocess.run(
        ["curl", "-sL", "--max-time", "15", "-H", f"PRIVATE-TOKEN: {token}", url],
        capture_output=True, text=True
    )
    try:
        return json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError:
        return []

# Discover repos where user has Developer+ access
projects = []
page = 1
while page <= 5:  # cap at 500 projects
    batch = fetch(f"{api}/projects?membership=true&min_access_level=30&simple=true&per_page=100&page={page}")
    if not isinstance(batch, list) or not batch:
        break
    projects.extend(batch)
    page += 1

results = []
for proj in projects:
    path = proj.get("path_with_namespace", "")
    encoded = urllib.parse.quote(path, safe="")
    mrs = fetch(f"{api}/projects/{encoded}/merge_requests?state=opened&per_page=30")
    if not isinstance(mrs, list):
        continue
    for mr in mrs:
        if mr["id"] in own_mrs_ids:
            continue
        author = mr.get("author", {}).get("username", "?")
        if not is_bot(author):
            continue
        results.append({
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
            "project_path": path,
            "roles": ["bot_unassigned"],
            "is_bot": True,
        })

json.dump(results, sys.stdout)
PYEOF
)

# --- Merge + fetch approvals + compute days_open ---

_API="$API" _TOKEN="$TOKEN" _OWN_MRS="$OWN_MRS" _BOT_MRS="$BOT_MRS" python3 << 'PYEOF'
import json, sys, subprocess, urllib.parse, os
from datetime import datetime, timezone

api = os.environ["_API"]
token = os.environ["_TOKEN"]
own_mrs_json = os.environ["_OWN_MRS"]
bot_json = os.environ["_BOT_MRS"]

own_mrs = json.loads(own_mrs_json) if own_mrs_json else []
bots = json.loads(bot_json) if bot_json else []
all_mrs = own_mrs + bots

now = datetime.now(timezone.utc)

for mr in all_mrs:
    # days_open
    try:
        created = datetime.fromisoformat(mr["created_at_full"])
        mr["days_open"] = (now - created).days
    except Exception:
        mr["days_open"] = 0

    # repo_name (last segment of project_path)
    pp = mr.get("project_path", "")
    mr["repo_name"] = pp.rsplit("/", 1)[-1] if pp else "?"

    # approvals (skip drafts)
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
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "10", "-H", f"PRIVATE-TOKEN: {token}",
             f"{api}/projects/{encoded}/merge_requests/{mr['iid']}/approvals"],
            capture_output=True, text=True,
        )
        data = json.loads(r.stdout)
        mr["approvals"] = len(data.get("approved_by", []))
        mr["approved_by"] = [a["user"]["username"] for a in data.get("approved_by", [])]
        mr["approvals_left"] = data.get("approvals_left", "?")
    except Exception:
        mr["approvals"] = "?"
        mr["approved_by"] = []
        mr["approvals_left"] = "?"

# Remove internal field before output
for mr in all_mrs:
    mr.pop("created_at_full", None)

json.dump(all_mrs, sys.stdout, indent=2)
PYEOF
