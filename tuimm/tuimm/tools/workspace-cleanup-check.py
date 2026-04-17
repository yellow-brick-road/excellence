#!/usr/bin/env python3
"""Workspace cleanup checker — scans ~/.kiro/temp/mr/ and ~/.kiro/temp/dev/ for stale workspaces.

Checks GitLab API for MR/branch status. Outputs JSON to stdout.
Designed to run in background via bg tool at session start.

Env vars:
  GITLAB_PERSONAL_ACCESS_TOKEN (required)
  GITLAB_API_URL (optional, default: https://source.tui/api/v4)
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TEMP_BASE = Path.home() / ".kiro" / "temp"
MR_DIR = TEMP_BASE / "mr"
DEV_DIR = TEMP_BASE / "dev"

TOKEN = os.environ.get("GITLAB_PERSONAL_ACCESS_TOKEN", "")
API_URL = os.environ.get("GITLAB_API_URL", "https://source.tui/api/v4").rstrip("/")


def load_user_projects() -> dict[str, str]:
    """Return {repo_name: project_path} from user's GitLab projects (Developer+ access)."""
    mapping = {}
    page = 1
    while page <= 5:
        data = gitlab_get(f"/projects?membership=true&min_access_level=30&simple=true&per_page=100&page={page}")
        if not data or not isinstance(data, list) or not data:
            break
        for proj in data:
            path = proj.get("path_with_namespace", "")
            name = proj.get("path", "")
            if name and path:
                mapping[name] = path
        page += 1
    return mapping


def gitlab_get(path: str) -> list | dict | None:
    """GET request to GitLab API. Returns parsed JSON or None on error."""
    url = f"{API_URL}{path}"
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def check_mr_workspaces(repos: dict[str, str]) -> list[dict]:
    """Check each mr-{iid}-{repo_name} dir against GitLab."""
    results = []
    if not MR_DIR.is_dir():
        return results

    for d in sorted(MR_DIR.iterdir()):
        if not d.is_dir():
            continue
        m = re.match(r"mr-(\d+)-(.+)", d.name)
        if not m:
            results.append({"dir": str(d), "type": "mr", "status": "unknown", "reason": "bad dir name"})
            continue

        iid, repo_name = m.group(1), m.group(2)
        project_path = repos.get(repo_name)
        if not project_path:
            results.append({"dir": str(d), "type": "mr", "iid": int(iid), "repo": repo_name, "status": "unknown", "reason": "repo not in user's projects"})
            continue

        encoded = urllib.parse.quote(project_path, safe="")
        data = gitlab_get(f"/projects/{encoded}/merge_requests?iids[]={iid}&state=all")
        if not data or not isinstance(data, list) or len(data) == 0:
            results.append({"dir": str(d), "type": "mr", "iid": int(iid), "repo": repo_name, "status": "unknown", "reason": "API error or MR not found"})
            continue

        mr = data[0]
        state = mr.get("state", "unknown")
        entry = {
            "dir": str(d),
            "type": "mr",
            "iid": int(iid),
            "repo": repo_name,
            "status": state,
            "title": mr.get("title", ""),
        }
        if state == "merged":
            entry["merged_at"] = mr.get("merged_at", "")
            entry["cleanable"] = True
        elif state == "closed":
            entry["closed_at"] = mr.get("closed_at", "")
            entry["cleanable"] = True
        else:
            entry["cleanable"] = False

        results.append(entry)

    return results


def check_dev_workspaces(repos: dict[str, str]) -> list[dict]:
    """Check each {TICKET}-{repo_name} dir — is the branch merged?"""
    results = []
    if not DEV_DIR.is_dir():
        return results

    for d in sorted(DEV_DIR.iterdir()):
        if not d.is_dir():
            continue

        # Get current branch
        try:
            branch = subprocess.check_output(
                ["git", "-C", str(d), "branch", "--show-current"],
                stderr=subprocess.DEVNULL, timeout=5
            ).decode().strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            results.append({"dir": str(d), "type": "dev", "status": "unknown", "reason": "not a git repo"})
            continue

        # Extract repo name from dir name (last segment after ticket ID)
        parts = d.name.split("-", 1)
        if len(parts) < 2:
            repo_name = d.name
        else:
            # Try to find repo name — dir is {TICKET}-{repo_name}
            # TICKET could be DIS-1234, so we need to be smarter
            # Look for a known repo name at the end
            repo_name = None
            for rn in repos:
                if d.name.endswith(f"-{rn}") or d.name.endswith(rn):
                    repo_name = rn
                    break
            if not repo_name:
                repo_name = d.name

        project_path = repos.get(repo_name)
        if not project_path:
            results.append({"dir": str(d), "type": "dev", "branch": branch, "repo": repo_name, "status": "unknown", "reason": "repo not in user's projects"})
            continue

        # Check if there's a merged MR for this branch
        encoded = urllib.parse.quote(project_path, safe="")
        data = gitlab_get(f"/projects/{encoded}/merge_requests?source_branch={urllib.parse.quote(branch)}&state=merged")
        if data and isinstance(data, list) and len(data) > 0:
            mr = data[0]
            results.append({
                "dir": str(d),
                "type": "dev",
                "branch": branch,
                "repo": repo_name,
                "status": "merged",
                "merged_at": mr.get("merged_at", ""),
                "mr_iid": mr.get("iid"),
                "title": mr.get("title", ""),
                "cleanable": True,
            })
        else:
            results.append({
                "dir": str(d),
                "type": "dev",
                "branch": branch,
                "repo": repo_name,
                "status": "active",
                "cleanable": False,
            })

    return results


def main():
    if not TOKEN:
        print(json.dumps({"error": "GITLAB_PERSONAL_ACCESS_TOKEN not set", "mr": [], "dev": []}))
        sys.exit(1)

    repos = load_user_projects()
    mr_results = check_mr_workspaces(repos)
    dev_results = check_dev_workspaces(repos)

    cleanable = [r for r in mr_results + dev_results if r.get("cleanable")]

    output = {
        "mr": mr_results,
        "dev": dev_results,
        "cleanable_count": len(cleanable),
        "total_workspaces": len(mr_results) + len(dev_results),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
