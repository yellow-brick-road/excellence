# $planner_autobuild — Execute a large plan in parallel with autobuild

## Triggers

"autobuild", "run in parallel", "generate tests for the whole project", "migrate all repos", "audit everything", any task too large for a single agent session.

## Prerequisites

- Read the `autobuild-reference` skill (engine.py, kiro.py)
- Read the `bg-reference` skill (bg.py)
- Read the `logd-reference` skill (logd.py) for monitoring
- Verify tools are available: `ls ~/.kiro/skills/tuimm-autobuild-reference/scripts/engine.py`

## Flow

### Phase 1 — UNDERSTAND (do NOT skip)

Ask the user questions before doing anything:

1. **What's the goal?** — "generate tests", "migrate to new library", "audit accessibility", etc.
2. **What's the scope?** — whole repo, specific folder, list of files, multiple repos?
3. **What's the input?** — code files, documents, PDFs, Jira tickets, existing specs?
4. **What's the expected output?** — test files, MRs, reports, documentation?
5. **Any constraints?** — exclude patterns, specific frameworks, style references?
6. **Parallelism preference?** — how many workers? (default: 4, limited by ~400MB RAM per process)

Do NOT proceed until the user confirms understanding.

### Phase 2 — ANALYZE

Scan the scope and present findings:

1. Inventory what exists (files, tests, configs, etc.)
2. Identify what needs to be done (gaps, missing items)
3. Group into logical tasks (by module, by type, by dependency)
4. Present a summary: "X items found, Y need work, Z groups"

### Phase 3 — PLAN

Generate the execution plan. Present to user BEFORE generating task files:

1. **DAG design** — maximize parallelism in early waves, synthesis tasks wait for inputs
   - Foundation tasks (no deps) → Wave 1
   - Dependent tasks → subsequent waves
   - Gate task at the end (consolidation, cleanup)

2. **Task breakdown** — for each task:
   - What it reads (source files, KBs, references)
   - What it produces (output files)
   - Dependencies (which tasks must finish first)
   - Estimated timeout
   - Domain-specific review checklist

3. **Configuration:**
   - Workers: user preference or default 4 (RAM: ~400MB per kiro-cli process)
   - Model: sonnet for speed, opus for quality — ask user
   - Review: "none" (review is INSIDE each task, domain-specific)
   - Max retries: 5
   - Per-task timeouts: short (120s), standard (300s), heavy (600s), very heavy (900s+)
   - **Note:** The autobuild.json config file goes inside the tasks directory. Engine loads it automatically.

4. **Present the plan clearly:**
   ```
   📋 Plan: [goal]
   📊 [N] tasks in [M] waves, [W] parallel workers
   ⏱️  Estimated: [time]
   
   Wave 1 (parallel): task-01, task-02, task-03, task-04
   Wave 2 (parallel): task-05(→01), task-06(→02,03)
   Wave 3: task-07(→05,06) [GATE — consolidation]
   ```

5. **Ask for approval.** Accept adjustments. Do NOT proceed without explicit "go".

### Phase 4 — PREPARE

After user approves:

1. **Index knowledge bases** if tasks need semantic search over documents/code:
   - Use `knowledge add` for source materials
   - KBs are workspace-persistent — spawned processes will see them
   - Note which KBs were created (for cleanup later)

2. **Generate task files** following the task template (see `planner-autobuild-task` template). Each task file MUST have:
   - Frontmatter: deps, timeout, creates, gate (boolean)
   - Self-contained mission brief (agent needs NO prior context)
   - Investigate section (what to read/search BEFORE doing anything)
   - Execute section (what to produce, exact output path)
   - Auto-review section (max 2 iterations, domain-specific checklist, every claim needs a source)
   - Notes section (what changed and why, for traceability)

3. **Generate autobuild.json** config file

4. **CRITICAL — No shared files between parallel tasks.** Each task writes to its own output file. If consolidation is needed, use a gate task that runs after all others.

### Phase 5 — PRE-FLIGHT REVIEW

Launch 4 parallel review subagents, each checking a different aspect:

| Reviewer | Checks |
|----------|--------|
| Structure | DAG correctness, all deps exist, no circular deps, coverage (every item in scope has a task) |
| Content | File paths exist, KB IDs valid, output paths don't collide, nothing missing from task prompts |
| Consistency | All tasks use same output format, same review checklist structure, cross-references are valid |
| Execution | Timeouts realistic, RAM budget OK, no race conditions on shared files, autobuild binary exists |

Fix ALL issues found. Re-run pre-flight if changes were significant.

### Phase 6 — LAUNCH

```bash
python3 ~/.kiro/skills/tuimm-autobuild-reference/scripts/engine.py \
  .autobuild/tasks/ \
  --bg
```

Inform the user:
```
🚀 Launched. [N] tasks, [M] waves, [W] workers.

Monitoring:
  python3 ~/.kiro/skills/tuimm-autobuild-reference/scripts/engine.py .autobuild/tasks/ --status     → progress by wave
  python3 ~/.kiro/skills/tuimm-autobuild-reference/scripts/engine.py .autobuild/tasks/ --tail       → live log of current task
  python3 ~/.kiro/skills/tuimm-autobuild-reference/scripts/engine.py .autobuild/tasks/ --stop       → stop gracefully

I'll check back when it finishes.
```

### Phase 7 — REPORT & CLEANUP

When autobuild completes:

1. **Report results:**
   - Tasks completed vs failed
   - Output files created
   - Tasks that need manual review (failed after max retries)
   - Gate task results (consolidation)

2. **Cleanup:**
   - Remove KBs that were created for this run (`knowledge remove`)
   - Optionally remove task files (.autobuild/ directory)
   - Keep output files

3. **Present using the `planner-autobuild-report` template**

## Rules

- NEVER launch without user approval of the plan
- NEVER skip pre-flight review
- ALWAYS cap auto-review at 2 iterations per task (prevents infinite loops)
- ALWAYS use per-task output files, never shared files between parallel tasks
- ALWAYS clean up KBs created for the run
- ALWAYS set review: "none" in autobuild config (review is inside tasks, not generic)
- If pre-flight finds blockers, fix them and re-run pre-flight. Do NOT launch with known issues
