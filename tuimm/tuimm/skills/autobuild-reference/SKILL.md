---
name: autobuild-reference
description: |
  autobuild — task engine at ~/.kiro/tuimm/tools/autobuild/ for executing markdown task files via kiro-cli agents.
  Use when: running multi-step pipelines, executing .plan/ output, building tools via task files,
  checking pipeline status, retrying failed tasks, understanding autobuild.json config.
  Contains: CLI reference, task file format, autobuild.json config, review modes, execution cycle.
---

# autobuild — Task Engine

Reads a folder of markdown task files and executes each through kiro-cli agents via ACP. Handles retries, gate tasks, progress persistence, parallel waves, and configurable review.

## Location

```
~/.kiro/tuimm/tools/autobuild/
  engine.py    # CLI + task engine
  kiro.py      # ACP client (kiro-cli wrapper)
```

Command: `autobuild` (symlinked to `~/.local/bin/autobuild`)

## CLI

```bash
autobuild tasks/                       # run all pending tasks
autobuild tasks/ --bg                  # run in background (via bg)
autobuild tasks/ --status              # rich progress table
autobuild tasks/ --tail                # tail log file
autobuild tasks/ --stop                # graceful stop
autobuild tasks/ --dry-run             # show execution plan
autobuild tasks/ --retry               # re-run failed tasks only
autobuild tasks/ --from 10             # resume from task 10_*
autobuild tasks/ --only 02             # run single task
autobuild tasks/ --reset 01            # reset one task to pending
autobuild tasks/ --reset-all           # reset everything
autobuild tasks/ --report              # JSON summary
autobuild tasks/ --makefile            # generate Makefile

# Overrides
autobuild tasks/ --agent tuimm_dev
autobuild tasks/ --model claude-opus-4.6
autobuild tasks/ --review none         # skip review phase
autobuild tasks/ --workers 3           # parallel wave concurrency
```

## Task File Format

Tasks are markdown files in a folder. Order by filename prefix (`00_`, `01_`, `10_`).

### Minimal (no frontmatter)

```markdown
# Setup MongoDB

Create a docker-compose.yml with MongoDB 7.0...
```

### With metadata

```markdown
---
verify: "docker compose ps --format json"
gate: true
creates: ["docker-compose.yml"]
agent: tuimm_dev
timeout: 300
deps: ["00", "01"]
type: test
---

# Setup MongoDB

Create a docker-compose.yml with MongoDB 7.0...
```

### Frontmatter fields

| Field | Default | Description |
|-------|---------|-------------|
| `deps` | Previous task | Dependencies (list of prefixes) |
| `verify` | None | Shell command to verify success |
| `gate` | false | Stop pipeline if this task fails |
| `creates` | [] | Files that must exist after execution |
| `agent` | From config | Override agent for this task |
| `timeout` | 600 | Seconds per kiro-cli call |
| `type` | "" | Used by agent_map routing |

## Project Config (autobuild.json)

Optional file in project root:

```json
{
  "agent": "tuimm_default",
  "model": "claude-sonnet-4.6",
  "review": "final",
  "max_retries": 3,
  "timeout": 600,
  "parallel": { "max_workers": 3 },
  "agent_map": {
    "default": "tuimm_default",
    "rules": [
      { "match": { "type": "test" }, "agent": "tui_test_writer" },
      { "match": { "folder": "tasks/infra/" }, "agent": "tui_infra" },
      { "match": { "pattern": "*_deploy*" }, "agent": "tui_deploy" }
    ]
  },
  "health": {
    "builtin": true,
    "checks": [
      { "name": "vpn", "cmd": "ping -c1 -W2 source.tui", "required": true }
    ]
  }
}
```

### Agent priority

```
CLI --agent > task frontmatter > agent_map rules > autobuild.json "agent" > tuimm_default
```

## Review Modes

| Mode | Phases | Description |
|------|--------|-------------|
| `none` | PLAN → EXECUTE → VERIFY | No LLM review. Fast. |
| `final` | PLAN → EXECUTE → VERIFY → REVIEW | Self-review at end (default) |

## Execution Cycle (per task)

1. **Pre-verify** — skip if task already done (verify passes + creates exist)
2. **PLAN** — agent reads task, proposes plan (once, reused across retries)
3. **EXECUTE** — agent implements the plan
4. **VERIFY** — run verify command + check creates + syntax check (.py/.json)
5. **REVIEW** — agent reviews own work → PASS/FAIL (final mode only)
6. On failure → retry from EXECUTE with error context (up to max_retries)
7. Gate tasks → stop pipeline on failure

### Error context accumulation

Failed attempts are saved to `context/{task}/error_{N}.md` with structured details (verify output, file checks, syntax errors). On retry, ALL previous errors are included in the prompt.

## Artifacts

```
.auto-build/              # gitignore this
  progress.json           # per-task state (atomic writes)
  results.tsv             # summary table
  .lock                   # instance lock (PID)
  context/                # kiro-cli outputs
    00_setup/
      plan_1.md
      exec_1.md
      review_1.md
      error_1.md          # if failed
```

## Health Checks

Run before first task. Built-in checks:
- kiro-cli in PATH
- logd running
- Disk space > 1GB

Custom checks via `health.checks[]` in autobuild.json.

## Dependencies

- logd (`~/.kiro/tuimm/tools/logd/`) — structured logging
- bg (`~/.kiro/tuimm/tools/bg/`) — background execution (--bg/--status/--tail/--stop)
- kiro-cli in PATH with ACP support
- Python 3.10+, stdlib only
