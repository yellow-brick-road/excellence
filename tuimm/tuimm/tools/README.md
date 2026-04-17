# Tools

Standalone scripts and utilities that agents invoke at runtime via shell commands. These are not AI — they're regular Python/Bash scripts that do mechanical work.

## Tools

| Tool | What it does | Used by |
|------|-------------|---------|
| **guidelines-generator/** | Extracts coding conventions from real code via AI. Scans a repo, classifies files, and produces guideline documents per category. Supports Nuxt, Java, Python, Go | `$qg_generate-guidelines` |
| **autobuild/** | Task engine that executes markdown task files through kiro-cli agents. Processes tasks in waves, handles retries, produces structured logs | `$planner_decompose` |
| **bg/** | Background execution library. Adds `--bg`/`--status`/`--stop` to any Python script | Any long-running tool |
| **logd/** | Structured log daemon (UDP + SQLite) and client library. Correlates logs across parent/child processes | Observability, autobuild |
| **gitlab-list-mrs.sh** | Queries GitLab API for MRs across multiple repos (reviewer, assignee, author, bots) | `$mr_list` |
| **tracked-repos.txt** | List of GitLab project paths to monitor for bot MRs | `gitlab-list-mrs.sh` |
| **workspace-cleanup-check.py** | Scans `~/.kiro/temp/` for stale workspaces, checks GitLab for merged MRs | Session start (background) |

## How they're invoked

Agents run tools via shell commands in their workflow:

```bash
python3 ~/.kiro/tuimm/tools/guidelines-generator/guidelines-generator.py --scan
bash ~/.kiro/tuimm/tools/gitlab-list-mrs.sh --reviewer
```

Tools are not loaded as resources — they're executed directly.
