# Tool: autobuild

Task engine that executes multi-step pipelines via kiro-cli agents.

## What it is

A global CLI tool that reads a folder of task files (markdown), and executes each through a configurable review pipeline using kiro-cli as the execution backend. Handles retries, gate tasks, progress persistence, context accumulation, and multi-agent debate.

Two components:
- `engine.py` — CLI + task loop, progress tracking, dependency resolution, review orchestration
- `kiro.py` — kiro-cli wrapper with two backends: subprocess (v1) and ACP (v2)

### Connection to Spec-Driven Dev

Autobuild is the execution engine for agent-generated plans. When an agent produces a plan in `.plan/` with discrete task steps, autobuild can consume those tasks. The relationship:
- **Agent** produces the plan (PLAN.md with ordered steps)
- **Autobuild** executes the plan through kiro-cli with configurable review pipelines
- **Review modes** complement plan approval: the plan is approved before execution, autobuild's review modes validate execution quality

## Dependencies

| Tool | Why |
|------|-----|
| logd | Structured logging of all phases, kiro calls, review rounds |
| bg | Background execution (--bg/--status/--tail/--stop) |

Also requires `kiro-cli` installed and available in PATH.

## Install path

```
~/.kiro/tools/autobuild/
  engine.py     # CLI + task engine
  kiro.py       # kiro-cli subprocess wrapper
```

Installed via `tui ai install tools autobuild` (resolves deps: logd → bg → autobuild).

## Usage

No per-project Python files. Run from any project root:

```bash
autobuild tasks/
autobuild tasks/ --bg
autobuild tasks/ --from 10
autobuild tasks/ --only 02
```

## Task files

Tasks are markdown files in a folder. Order determined by filename prefix.

### Minimal task (no frontmatter)

```markdown
# Setup MongoDB with Docker

Create a docker-compose.yml with MongoDB 7.0, port 27017...
```

### Task with metadata (optional frontmatter)

```markdown
---
verify: "docker compose ps --format json"
gate: true
creates: ["docker-compose.yml"]
agent: personal_dev
timeout: 300
deps: ["00", "01"]
---

# Setup MongoDB with Docker

Create a docker-compose.yml with MongoDB 7.0...
```

### Conventions (defaults)

| Field | Default | Override in frontmatter |
|-------|---------|------------------------|
| Order | Numeric prefix (`00_`, `01_`, `10_`) | — |
| Deps | Linear (each task depends on previous) | `deps: ["00", "01"]` |
| Verify | None (review phase only) | `verify: "command"` |
| Gate | `false` | `gate: true` |
| Creates | None | `creates: ["file.py"]` |
| Agent | From config or `tui_default` | `agent: personal_dev` |
| Timeout | 600s | `timeout: 300` |

## Project config (optional)

`autobuild.json` in project root:

```json
{
  "agent": "tui_default",
  "model": "claude-opus-4.6",
  "review": "final",
  "max_retries": 3,
  "timeout": 600,
  "agent_map": {
    "default": "tui_default",
    "rules": [
      { "match": { "type": "test" }, "agent": "tui_test_writer" },
      { "match": { "type": "infra" }, "agent": "tui_infra" },
      { "match": { "folder": "tasks/frontend/" }, "agent": "tui_frontend" },
      { "match": { "pattern": "*_test_*" }, "agent": "tui_test_writer" }
    ]
  },
  "health": {
    "builtin": true,
    "checks": [
      { "name": "vpn", "cmd": "ping -c1 -W2 source.tui", "required": true },
      { "name": "docker", "cmd": "docker info", "required": false }
    ],
    "recheck": false
  }
}
```

If not present, global defaults apply.

### Agent priority

```
CLI flag > task frontmatter > agent_map rules > autobuild.json "agent" > tui_default
```

### Agent mapping

For projects with many similar tasks, `agent_map` routes tasks to specialized agents based on metadata. Match criteria:

| Criterion | Source | Example |
|-----------|--------|---------|
| `type` | Task frontmatter `type:` field | `{ "match": { "type": "test" }, "agent": "tui_test_writer" }` |
| `folder` | Task file path | `{ "match": { "folder": "tasks/infra/" }, "agent": "tui_infra" }` |
| `pattern` | Filename glob | `{ "match": { "pattern": "*_test_*" }, "agent": "tui_test_writer" }` |

First match wins. Falls back to `agent_map.default`, then `agent`, then `tui_default`.

Proven pattern: b2c-frontend migration maps file types (utility, store, component, page, test) to 7 specialized migration agents, each with tailored steering and examples for its file type.

### Health checks

Run once before the first task. Built-in checks (when `builtin: true`):
- `kiro-cli` in PATH
- logd daemon running
- Disk space > 1GB

Custom checks: shell commands in `health.checks[]`. `required: true` = abort pipeline if fails. `required: false` = warn and continue. With `recheck: true`, health checks re-run between tasks.

## Review modes

| Mode | Phases | Calls/task | Use case |
|------|--------|------------|----------|
| `none` | PLAN → EXECUTE → VERIFY | ~3 | Prototyping, trust the agent |
| `final` | PLAN → EXECUTE → VERIFY → REVIEW | ~4 | Default. Single review at the end |
| `extended` | PLAN+review → EXECUTE+review → VERIFY → VERDICT | ~6-8 | Review after each phase, builder+reviewer |
| `full` | PLAN(candidates)+panel → EXECUTE+panel → VERIFY → PANEL VERDICT | ~15-25 | Paranoid. Multi-agent debate until consensus |

### Mode: none

```
PLAN    → kiro-cli reads task file, generates plan
EXECUTE → kiro-cli implements the plan
VERIFY  → verify command + check creates
```

No LLM review. Only automated verification. Fast and cheap.

### Mode: final

```
PLAN    → kiro-cli generates plan
EXECUTE → kiro-cli implements
VERIFY  → automated checks
REVIEW  → kiro-cli reviews its own output → PASS/FAIL
```

Single self-review at the end. If FAIL → retry from EXECUTE with error context.

### Mode: extended

Two roles: Builder and Reviewer.

```
PLAN:
  Builder   → generates plan
  Reviewer  → critiques plan (gaps? correct approach?)
  Builder   → revises plan if issues

EXECUTE:
  Builder   → implements
  Reviewer  → reviews code (bugs? edge cases? quality?)
  Builder   → applies fixes if issues

VERIFY:
  (automated — shell commands, file checks)

VERDICT:
  Reviewer  → PASS / FAIL with reasons
```

~6-8 kiro-cli calls per task. Review at every phase.

### Mode: full

Four roles: Builder, Reviewer, Architect, QA. Multiple plan candidates. Panel debate with rounds.

#### Roles

| Role | Perspective | Looks for | ACP permissions |
|------|-------------|-----------|-----------------|
| **Builder** | Implementer | Executes and defends decisions | `allow_all` (fs + terminal) |
| **Reviewer** | Code quality | Bugs, edge cases, readability | `fs.read` only |
| **Architect** | Design | Patterns, scalability, coupling | `fs.read` only |
| **QA** | Testing/Security | Missing tests, vulnerabilities, malicious inputs | `fs.read` + `terminal` (for verify commands) |

#### Flow

```
PLAN:
  Builder A → plan A  ┐
  Builder B → plan B  ├→ Panel selects best plan
  Builder C → plan C  ┘

  ┌─ Debate (max N rounds) ──────────────────────┐
  │  Reviewer:   "Missing error handling in X"     │
  │  Architect:  "This couples Y with Z"           │
  │  QA:         "No test plan"                    │
  │  Builder:    "Fixed X, decoupled Y. Tests in   │
  │               next task"                       │
  │                                                │
  │  Reviewer:   "X OK. Approved ✓"               │
  │  Architect:  "Decoupled. Approved ✓"           │
  │  QA:         "Acceptable. Approved ✓"          │
  └─ Consensus reached ───────────────────────────┘

EXECUTE:
  Builder (winner) → implements the consensus plan

  ┌─ Debate ──────────────────────────────────────┐
  │  (same cycle: feedback → fix → check)          │
  │  Until all 3 reviewers approve                 │
  └───────────────────────────────────────────────┘

VERIFY:
  (automated)

VERDICT:
  Full panel → unanimous vote required
  No consensus after max rounds → FAIL + log disagreements
```

#### Candidates

Multiple builders generate plans independently in the PLAN phase. The panel (Reviewer + Architect + QA) votes on the best one. Number of candidates configurable via `candidates` field.

With ACP backend: `unstable_forkSession` can create session forks for each candidate, sharing the same base context without interference. Without ACP: separate subprocess calls with shared context files.

#### Config

```json
{
  "review": "full",
  "candidates": 3,
  "review_max_rounds": 3,
  "roles": {
    "builder": [
      { "model": "claude-opus-4.6" },
      { "model": "gemini-2.5-pro" },
      { "model": "gpt-5.2" }
    ],
    "reviewer":  { "model": "claude-sonnet-4" },
    "architect": { "model": "gemini-2.5-pro" },
    "qa":        { "model": "gpt-5.2" }
  }
}
```

If `roles` not defined, all roles use the project's default agent/model with different prompts.

If `builder` is an array, each entry generates a candidate plan. Array length overrides `candidates`.

#### Cost estimate

| Mode | Calls/task | ~Time/task | 33 tasks |
|------|------------|------------|----------|
| `none` | 3 | 5 min | ~2.5h |
| `final` | 4 | 7 min | ~4h |
| `extended` | 6-8 | 12 min | ~7h |
| `full` (3 candidates, 3 rounds) | 15-25 | 25-40 min | ~15-20h |

Full mode is designed for overnight background runs.

## Execution cycle (per task)

Regardless of review mode, the core cycle per task:

1. **Check deps** — all dependency tasks must be `passed`
2. **Run phases** — according to review mode (see above)
3. **On failure** — retry from EXECUTE with error context (up to `max_retries`)
4. **Gate tasks** — if `gate: true` and task fails after all retries, pipeline stops
5. **TODO scan** — scan created/modified files for `TODO(autobuild)` markers, log as warnings
6. **Update progress** — mark task as `passed` or `failed` in progress.json

### Parallel execution

Tasks with no dependencies between them can run in parallel waves. The engine resolves the dependency graph and groups independent tasks into waves:

```
Wave 1: [T-00]              # no deps
Wave 2: [T-01, T-02, T-03]  # all depend only on T-00
Wave 3: [T-04]              # depends on T-01 and T-02
```

Within a wave, tasks execute concurrently via `ThreadPoolExecutor`. Result logging is thread-safe (locked TSV writes). Configurable concurrency:

```json
{ "parallel": { "max_workers": 3 } }
```

Default: sequential (1 worker). Set `max_workers > 1` to enable parallel waves.

Proven pattern: b2c-frontend migration runs parallel ACP agents per wave, processing multiple files simultaneously with thread-safe result tracking.

### Context accumulation

Each task's PLAN prompt includes:
- The task markdown file
- Outputs from completed dependency tasks (from `context/`)
- Error context from previous failed attempts (for retries)
- Project-level context (autobuild.json, README, etc.)

### Error context accumulation

When a task fails, the full kiro-cli output is saved to `context/{task}/error_{attempt}.md`. On retry, ALL previous error files are included in the prompt so the agent doesn't repeat the same mistakes:

```
context/T-02/
  plan_1.md       # first attempt plan
  error_1.md      # first attempt: full output showing what went wrong
  plan_2.md       # second attempt plan (informed by error_1)
  error_2.md      # second attempt: different failure
  plan_3.md       # third attempt (informed by error_1 + error_2)
  exec_3.md       # third attempt succeeded
  review.md       # final review
```

This is different from logd: logd gets the structured error log (`level=ERROR, msg="task failed", data={error, traceback}`). Error files get the FULL agent output — pages of reasoning, tool calls, and failure context. logd for monitoring, error files for retry intelligence.

### TODO scanning

After each task completes, autobuild scans created/modified files for TODO markers:

```
TODO(autobuild): reason
TODO(migration): reason
```

Found TODOs are:
- Logged as warnings to logd
- Included in `results.tsv` (count per task)
- Summarized in `--report` output

**Steering requirement:** Agents must be instructed to use `TODO(autobuild)` markers when they can't fully implement something, instead of skipping silently. Add to `STEERING_CONVENTIONS.md`:

> When you cannot fully complete a requirement during autobuild execution, leave a `TODO(autobuild): <reason>` comment in the code. Never skip or silently omit functionality.

### Run-level state

Each pipeline run tracks its state in `progress.json`:

```json
{
  "run_uid": "20260313-1244-a3f",
  "started_at": "2026-03-13T12:44:51",
  "finished_at": null,
  "current_task": "T-02",
  "summary": {
    "total": 33,
    "passed": 5,
    "failed": 1,
    "pending": 27,
    "running": 1
  },
  "tasks": { ... }
}
```

Enables rich `--status` output: progress bar, current task, elapsed time, pass/fail counts.

## CLI

```bash
autobuild tasks/                       # run all pending tasks
autobuild tasks/ --bg                  # run in background (via bg)
autobuild tasks/ --from 10             # resume from task 10_*
autobuild tasks/ --only 02             # run single task
autobuild tasks/ --retry               # re-run only failed tasks
autobuild tasks/ --dry-run             # show plan without executing
autobuild tasks/ --status              # progress table
autobuild tasks/ --tail                # tail logs via logd (by uid)
autobuild tasks/ --stop                # graceful SIGTERM (via bg)
autobuild tasks/ --reset 01            # reset one task to pending
autobuild tasks/ --reset-all           # reset everything
autobuild tasks/ --report              # JSON summary
autobuild tasks/ --makefile            # generate Makefile with common commands

# Overrides
autobuild tasks/ --agent personal_dev
autobuild tasks/ --model claude-opus-4.6
autobuild tasks/ --review full
autobuild tasks/ --candidates 3
autobuild tasks/ --workers 3           # parallel wave concurrency
```

`--bg`, `--status`, `--tail`, `--stop` are handled by bg's `setup_bg()`.

### Makefile generation

`autobuild tasks/ --makefile` generates a `Makefile` in the project root with common commands:

```makefile
.PHONY: run status stop tail retry report

run:
	autobuild tasks/ --bg
status:
	autobuild tasks/ --status
stop:
	autobuild tasks/ --stop
tail:
	autobuild tasks/ --tail
retry:
	autobuild tasks/ --retry --bg
report:
	autobuild tasks/ --report
```

Proven pattern: both POCs use Makefiles as the user-facing entry point (`make run`, `make status`, `make stop`). Easier to remember than full CLI commands.

## Artifacts

Stored in `.auto-build/` in the project root (gitignored):

```
.auto-build/
  progress.json          # per-task state: pending/running/passed/failed
  results.tsv            # summary: task  status  attempts  duration
  context/               # kiro-cli outputs for retry context
    00_setup-db/
      plan_1.md          # plan output, attempt 1
      execute_1.md       # execute output, attempt 1
      review_1.md        # review output, attempt 1
      plan_candidates/   # full mode: candidate plans
        candidate_1.md
        candidate_2.md
        candidate_3.md
      debate/            # full mode: debate rounds
        round_1.md
        round_2.md
```

- Logs → logd (no queue.log)
- PID → bg (no .pid in .auto-build/)
- progress.json stores the current run uid for correlation

## kiro-cli wrapper (kiro.py)

Two backends: subprocess (v1, legacy) and ACP (v2, default). Engine calls the same API regardless.

### v1: Subprocess backend (legacy)

⚠️ Legacy. `--model` flag does NOT exist on `kiro-cli chat`. Use ACP backend instead.

```python
from kiro import kiro, KiroResult

result = kiro(
    prompt="Implement the gather script...",
    agent="tui_default",
    timeout=600,
    uid="20260313-1244-a3f"
)
# result.success, result.output, result.exit_code, result.duration
```

- Calls `kiro-cli chat --no-interactive -a --agent X "prompt"`
- Sets `LOGD_UID` env var on subprocess for log correlation
- Strips ANSI escape codes from output
- Handles timeout (`subprocess.TimeoutExpired`)
- Logs call start/end/timeout to logd

Limitations:
- No `--model` flag (only exists on `kiro-cli acp`)
- One subprocess per call (3-25 per task depending on review mode)
- Text-only output — no structured data about tool calls or file operations
- No streaming visibility during execution
- No tool permission control
- Cancellation via SIGTERM (no graceful shutdown)

### v2: ACP backend (default)

Uses Agent Client Protocol (JSON-RPC over stdio) for structured communication. See `ideas/ai/ACP_INTEGRATION.md` for full architecture.

Working reference implementation: `~/showmethemoney/poc.newspaper/scripts/lib/acp.py` (production-tested, used by all pipeline scripts).

**Proven in POCs:** Both `poc.newspaper` (33 tasks, auto-build pipeline) and `b2c-frontend` (Nuxt 2→4 migration, 200+ files across 7 phases) use ACP as the execution backend. Validated: agent reuse across prompts, parallel waves, graceful cancellation, error recovery.

```python
from lib.acp import AcpAgent

# One agent per task (or reuse across tasks for same agent type)
agent = AcpAgent(agent="tui_default", model="claude-opus-4.6", cwd=project_root)
text = agent.prompt("Implement the gather script...", timeout=600)
agent.close()
```

Key class: `AcpAgent(agent, model, cwd)`:
- Spawns `kiro-cli acp --agent X --model Y --trust-all-tools`
- Handles initialize → session/new → prompt → collect agent_message_chunks → return text
- Auto-approves permissions (allow_all)
- Implements fs/read_text_file and fs/write_text_file callbacks
- `.cancel()` for graceful cancellation, `.close()` for cleanup
- `.alive` property to check subprocess health

Parallel execution via `run_wave(run_fn, count, timeout)` using ThreadPoolExecutor.

Gains over v1:
- `--model` flag works (only exists on `kiro-cli acp`)
- Single process per agent, reusable across prompts (no 4s startup overhead per call)
- Structured JSON output — no ANSI stripping, no text parsing
- Real-time streaming via agent_message_chunk events
- Permission control per role (Builder: allow_all, Reviewer: read-only)
- Graceful cancellation via `session/cancel`
- Agent switching without respawning (`session/set_mode`)
- Session forking for candidate plans in `full` mode (`unstable_forkSession`)

### Backend selection

```json
// autobuild.json
{
  "backend": "acp"
}
```

| Value | Backend | When |
|-------|---------|------|
| `acp` | v2 kiro-cli acp | Default. Structured output, model selection, streaming, permissions |
| `subprocess` | v1 kiro-cli chat | Legacy fallback only. No model selection |

Engine doesn't care which backend — both return text output. ACP provides structured events during execution.

## uid integration

- Pipeline run generates a uid via logd at startup
- Stored in `progress.json` as `run_uid`
- Passed to all kiro-cli calls via `LOGD_UID` env var
- All logs from the run are queryable: `logd.py tail --uid {run_uid}`

## Project structure

```
my-project/
  tasks/                    # you create this
    00_setup-db.md
    01_db-cli.md
    02_gate-test.md
    ...
  autobuild.json            # optional project config
  .auto-build/              # engine creates this (gitignored)
    progress.json
    results.tsv
    context/
```

## POC references

These implementations informed the design extensions above:

| POC | Path | What it proved |
|-----|------|---------------|
| poc.newspaper | `~/showmethemoney/poc.newspaper/scripts/auto-build.py` | 33-task pipeline, ACP backend, final review mode, error retry with context accumulation, bg execution, logd integration |
| b2c-frontend migration | `~/work/b2c-frontend/tasks/migrate/coordinator.py` | 200+ file migration, wave-based parallel execution, agent mapping per file type, phase-based runs, state management, health checks, thread-safe logging, --retry for failures |

Key shared libraries extracted from POCs:
- `lib/acp.py` — ACP client (JSON-RPC over stdio), proven in both projects
- `lib/bg.py` — background execution, adapted per project (fecha vs phase identifiers)
- `lib/state.py` — run-level state tracking (b2c-frontend)
- `lib/health.py` — pre-execution health checks (b2c-frontend)

## Requirements

- Python 3.10+
- No pip dependencies (stdlib only)
- logd installed (`~/.kiro/tools/logd/`)
- bg installed (`~/.kiro/tools/bg/`)
- kiro-cli in PATH

## Registry manifest

```json
{
  "name": "autobuild",
  "version": "2.0.0",
  "deps": ["logd", "bg"],
  "install_path": "~/.kiro/tools/autobuild",
  "files": ["engine.py", "kiro.py"],
  "requires": { "python": ">=3.10", "bin": ["kiro-cli"] }
}
```
