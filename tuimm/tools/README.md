# Tools

Standalone scripts that agents run via shell. Not AI — just Python and Bash doing mechanical work.

---

## guidelines-generator

Extracts coding conventions from a real codebase via AI. Scans committed files, asks an agent to propose categories, then extracts patterns per category through a 4-phase pipeline.

```bash
cd ~/work/my-project

# 1. Scan — see what's in the repo
python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --scan

# 2. Run the full pipeline in background
python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --phase all --bg -y

# 3. Check progress
python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --report

# 4. Stop if needed
python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --stop
```

Supports Nuxt/Vue/TS (default), Java (`--extensions '\.java$'`), Python, Go. The agent proposes categories based on the actual repo structure — you don't need to configure anything.

Output goes to `docs/guidelines/` in the project root.

Key flags:
- `--scan` — classify files, show table (no extraction)
- `--phase all` — run everything (extract → review → split → refine)
- `--bg` — run in background
- `--report` — show progress
- `--recategorize` — re-run agent category discovery
- `--reset-phase all` — start fresh

---

## autobuild

Task engine that executes markdown task files through kiro-cli agents. Used by the Planner agent to run multi-step plans.

```bash
# Run tasks from a plan
python3 ~/.kiro/tools/autobuild/engine.py --tasks .plan/my-feature/tasks/

# Check status
python3 ~/.kiro/tools/autobuild/engine.py --status
```

Tasks are markdown files with a description and acceptance criteria. Autobuild processes them in waves, respecting dependencies, with retry on failure.

---

## gitlab-list-mrs.py

Queries GitLab for MRs across multiple repos. Used by `$mr_list`.

```bash
python3 ~/.kiro/tools/gitlab-list-mrs.py [username]
```

Returns JSON. Requires `GITLAB_PERSONAL_ACCESS_TOKEN`. Auto-discovers your projects via GitLab API (projects with activity in last 90 days) — no config file needed.

---

## bg

Background execution library. Any Python script can import it to get `--bg`/`--status`/`--stop`/`--tail` support. Used by guidelines-generator and autobuild.

---

## logd

Structured log daemon (UDP + SQLite) and client library. Scripts send logs via UDP, the daemon stores them in SQLite. Useful for correlating logs across parent/child processes in long-running pipelines.

---

## workspace-cleanup-check.py

Runs at session start (background). Scans `~/.kiro/temp/` for stale agent workspaces and checks GitLab to see if their MRs were already merged.
