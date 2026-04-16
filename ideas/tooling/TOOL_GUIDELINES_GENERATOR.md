# Tool: guidelines-generator

Automated guidelines extraction pipeline for frontend repositories. Scans a codebase, classifies files by type, extracts generalizable conventions via AI agents, and produces consolidated guidelines documents.

Evolution of `___scripts/extract-patterns.py` (b2c-tuimusement-frontend, white-label-frontend) — rebuilt with autobuild/bg/logd integration.

## What it is

A CLI tool that reads committed files in a repo, extracts reusable patterns and conventions from them via AI, and produces structured guidelines documents in `docs/guidelines/`.

Not a linter. Not a style guide generator. A **pattern extractor** that turns implicit conventions (how the code IS written) into explicit guidelines (how code SHOULD be written).

### The problem it solves

Every repo has implicit conventions — patterns that emerged organically over time. New developers can't discover them without reading hundreds of files. AI agents can't follow them without explicit documentation. This tool makes the implicit explicit, automatically.

### Connection to Excellence

- Generates living documentation that stays in sync with actual code
- Output feeds into Excellence skills (e.g., `excellence_testing-nuxt-*` skills come from running this against test files)
- Distributed via TUI CLI (`tui fe guidelines`)
- Implements Auto Documentation practice (`ideas/practices/AUTO_DOCUMENTATION.md`)
- Reproducible: re-run when patterns change, guidelines update

## Dependencies

| Tool | Why |
|------|-----|
| autobuild | Task execution engine for phase 1 (parallel extraction with retry) |
| bg | Background execution (`--bg/--status/--stop`) |
| logd | Structured logging |
| kiro-cli | ACP backend for agent execution |

## File layout

```
~/.kiro/tools/guidelines-generator/
  guidelines-generator.py          # CLI entry point
  __tests__/                       # Unit tests

~/.kiro/templates/guidelines-generator/
  extract.md                       # Phase 1 task template (per file)
  review.md                        # Phase 2 task template (per category)
  split.md                         # Phase 3 task template (per category)

~/.kiro/skills/
  excellence_guidelines-generator/SKILL.md   # CLI reference
```

## Usage

```bash
# From any frontend repo root
guidelines-generator --scan                    # classify files, show table
guidelines-generator --phase all               # run all 3 phases
guidelines-generator --phase all --bg          # same, in background
guidelines-generator --phase extract           # phase 1 only
guidelines-generator --phase review            # phase 2 only
guidelines-generator --phase split             # phase 3 only
guidelines-generator --status                  # check progress
guidelines-generator --report                  # summary of generated guidelines

# Context filters
guidelines-generator --only tests              # only test files (*.spec.ts, *.test.ts)
guidelines-generator --only components         # only Vue components
guidelines-generator --only composables        # only composables
guidelines-generator --only stores             # only Pinia stores
guidelines-generator --only tests,components   # multiple types
guidelines-generator --dir src/features/booking  # only one directory
guidelines-generator --phase all               # everything in the repo

# Overrides
guidelines-generator --agent tui_default       # override agent (default: tui_default)
guidelines-generator --model claude-opus-4.6   # override model
guidelines-generator --workers 3               # parallel workers for phase 1
guidelines-generator --max-tasks 50            # limit extraction tasks

# Re-run
guidelines-generator --reset-phase review      # reset progress for a phase
guidelines-generator --reset-phase all         # reset everything
```

## Architecture

```
guidelines-generator.py (single file)
    │
    ├── scan(repo_path, filters) → FileInfo[]
    │     Walk repo, classify files, apply --only/--dir filters
    │
    ├── phase_extract(files) → raw/{type}/{filename}.md
    │     Generate autobuild tasks (one per file)
    │     Autobuild executes in parallel with retry
    │     Each task writes to its own file (no shared state)
    │
    ├── phase_review(categories) → reviewed/{type}.md
    │     For each category: read all raw/{type}/*.md
    │     Call kiro-cli to deduplicate, consolidate, structure
    │     Output: one reviewed file per category
    │
    ├── phase_split(categories) → docs/guidelines/{type}.md
    │     For each category: classify bullets as specific vs shared
    │     Write final guidelines to docs/guidelines/
    │     Shared patterns go to docs/guidelines/shared/
    │
    └── report() → summary
```

## Scanner

### File classification

The scanner classifies files into categories. Classification is deterministic — by path and content heuristics.

```python
@dataclass
class FileInfo:
    path: Path              # relative to repo root
    category: str           # classification
    loc: int                # lines of code
    skip_reason: str        # why skipped (if applicable)
```

### Category map

| Pattern | Category |
|---------|----------|
| `*.spec.ts`, `*.test.ts` | `tests` |
| `components/**/*.vue` | `components` |
| `composables/use*.ts` | `composables` |
| `stores/*.store.ts` | `stores` |
| `utils/**/*.ts`, `helpers/**/*.ts` | `utils` |
| `pages/**/*.vue` | `pages` |
| `middleware/**/*.ts` | `middleware` |
| `plugins/**/*.ts` | `plugins` |
| `services/**/*.ts`, `api/**/*.ts` | `services` |
| `server/**/*.ts` | `server` |
| `layouts/**/*.vue` | `layouts` |
| `constants/**/*.ts` | `constants` |
| `types/**/*.ts` | `types` |
| `config/**/*.ts` | `config` |

Configurable per repo via `.guidelines.json` (optional):
```json
{
  "categories": {
    "features": "features/**/*.{vue,ts}",
    "shared": "shared/**/*.{vue,ts}"
  },
  "exclude": ["__mocks__", "mock-server", "public"]
}
```

### Test sub-classification

When `--only tests`, the scanner further classifies test files by what they test. Output goes to `docs/guidelines/tests/{type}.md`:

| Detection | Sub-category | Output |
|-----------|-------------|--------|
| Tests in `composables/` or testing `use*.ts` | `tests/composables` | `docs/guidelines/tests/composables.md` |
| Tests importing `.vue` or using `mount`/`mountSuspended` | `tests/components` | `docs/guidelines/tests/components.md` |
| Tests with `createPinia`/`defineStore` | `tests/stores` | `docs/guidelines/tests/stores.md` |
| Tests in `utils/`/`helpers/` | `tests/utils` | `docs/guidelines/tests/utils.md` |
| Tests in `middleware/` | `tests/middleware` | `docs/guidelines/tests/middleware.md` |
| Tests in `services/`/`api/` | `tests/services` | `docs/guidelines/tests/services.md` |
| Tests in `plugins/` | `tests/plugins` | `docs/guidelines/tests/plugins.md` |

This enables generating testing guidelines per file type, which feed directly into `excellence_testing-nuxt-*` skills.

### File source

Uses `git ls-files --cached` to only process committed files (same as original extract-patterns.py). Ignores untracked, gitignored, and binary files.

### Filters

- `--only <types>` — comma-separated list of categories to include
- `--dir <path>` — only files under this directory
- Both can combine: `--only tests --dir src/features/booking`

## Phase 1: Extract

### How it works

1. Scanner produces `FileInfo[]`
2. For each file, generate an autobuild task .md from `templates/guidelines-generator/extract.md`
3. Run autobuild — parallel execution, retry on failure
4. Each task reads ONE source file, extracts patterns, writes to `raw/{category}/{filename}.md`

### Task template (extract.md)

```markdown
---
verify: "test -s {OUTPUT_PATH}"
creates: ["{OUTPUT_PATH}"]
timeout: 120
type: extract
---

# Extract guidelines from {SOURCE_PATH}

Read the file `{SOURCE_PATH}`.
This is a {CATEGORY} file in a {FRAMEWORK} project.

Extract ONLY generalizable, reusable conventions for writing new {CATEGORY}.
Focus on: structure, API choices, naming, styling, typing, patterns.

Format as short actionable rules (style-guide bullets).
Good: '- Use `<script setup lang="ts">` for all components'
Bad: '- This file imports useRoute from vue-router'

Output ONLY bullet points (- rule), one per line.
No commentary, no annotations, no reasoning.
If nothing useful, output EXACTLY: NONE

Write output to `{OUTPUT_PATH}`.
```

### Why autobuild for phase 1

- Hundreds of files to process (b2c-tuimusement-frontend has 500+ committed files)
- Each file is independent — perfect for parallel execution
- Retry handles transient kiro-cli failures
- Progress tracking survives interruptions
- `--bg` runs overnight if needed

### Output structure

```
.guidelines/                       # gitignore this
  autobuild.json
  tasks/
    001_useBooking.spec.md
    002_SearchButton.vue.md
    ...
  raw/
    components/
      SearchButton.vue.md
      BookingCard.vue.md
    composables/
      useBooking.ts.md
      useSearch.ts.md
    tests/                         # or nuxt-component-testing/ if --only tests
      useBooking.spec.md
      SearchButton.spec.md
    ...
  scan-results.json
```

## Phase 2: Review

### How it works

For each category in `raw/`, read all extracted files, pass to kiro-cli for consolidation.

This phase runs sequentially (one call per category, ~7-15 categories). Autobuild is overkill here.

### What the LLM does

1. Remove exact duplicates
2. Merge near-duplicates (same idea, different wording) → keep best version
3. Remove patterns too specific to one file (not generalizable)
4. Group related patterns under sub-headings (`## Topic`)
5. Keep bullet-point format

### Output

```
.guidelines/
  reviewed/
    components.md
    composables.md
    stores.md
    tests.md                       # or nuxt-component-testing.md etc.
    ...
```

## Phase 3: Split + Write

### How it works

For each reviewed category:
1. Classify each bullet as SPECIFIC (only this category) or SHARED (cross-cutting)
2. Write specific patterns to `docs/guidelines/{category}.md`
3. Write shared patterns to `docs/guidelines/shared/{topic}.md`

### Shared topics

Cross-cutting patterns that appear across categories:
- typescript, scss-styling, imports-aliases, documentation
- error-handling, logging, async-patterns, reactivity
- testing, naming, accessibility

### Output (final)

```
docs/guidelines/
  components.md                    # How to write components
  composables.md                   # How to write composables
  stores.md
  utils.md
  middleware.md
  plugins.md
  services.md
  shared/
    typescript.md                  # Cross-cutting TS patterns
    naming.md                      # Naming conventions
    error-handling.md
    ...
  tests/                           # Subsection: how to TEST each type
    components.md                  # How to test components
    composables.md                 # How to test composables
    stores.md
    utils.md
    middleware.md
    plugins.md
    services.md
```

Tests are a subsection, not a top-level category. `docs/guidelines/components.md` = how to write them. `docs/guidelines/tests/components.md` = how to test them.

### Guidelines → Skills pipeline

When running `--only tests`, the output maps to Excellence skills:

```
docs/guidelines/tests/components.md  →  excellence_testing-nuxt-component/SKILL.md
docs/guidelines/tests/composables.md →  excellence_testing-nuxt-composable/SKILL.md
docs/guidelines/tests/stores.md      →  excellence_testing-nuxt-store/SKILL.md
```

This copy/transform step can be manual or automated via a `--to-skills` flag:

```bash
guidelines-generator --only tests --phase all --to-skills
# Runs pipeline + copies final output to ~/.kiro/skills/excellence_testing-nuxt-*/
```

## Framework detection

The scanner reads `package.json` to detect the framework:

| Detection | Framework label |
|-----------|----------------|
| `nuxt` in dependencies | `Nuxt 4 + Vue 3 + TypeScript` |
| `nuxt` < 3 | `Nuxt 2 + Vue 2` |
| `react-native` or `expo` | `React Native + Expo + TypeScript` |
| None of the above | `TypeScript` |

The framework label is injected into extraction prompts for context.

## Comparison with legacy extract-patterns.py

| Feature | Legacy (___scripts/) | guidelines-generator |
|---------|---------------------|---------------------|
| Background | nohup + PID file | bg (setup_bg) |
| Logging | print + .queue.log | logd (structured, queryable) |
| Progress | Manual JSON | autobuild (progress.json) |
| Retry | Manual loop | autobuild (max_retries) |
| Parallel | Sequential only | autobuild (max_workers) |
| VPN check | Hardcoded PowerShell | Removed (not needed with proper retry) |
| Night mode | Hardcoded sleep | Removed |
| Categories | Hardcoded per repo | Auto-detected + configurable |
| Output | ___patterns/ in repo | docs/guidelines/ in repo |
| Scope | One repo at a time | Same, but generalizable |
| Filters | --category only | --only, --dir, combinable |

## Implementation Notes

### Single file

`guidelines-generator.py` — single Python file (~500 lines). Same pattern as testgen.py, engine.py, bg.py.

Sections:
1. Scanner (~120 lines) — walk, classify, filter
2. Phase 1 orchestrator (~80 lines) — generate tasks, run autobuild
3. Phase 2 orchestrator (~80 lines) — review calls
4. Phase 3 orchestrator (~100 lines) — split + write to docs/guidelines/
5. CLI (~70 lines) — argparse, bg integration
6. Report (~50 lines) — progress summary

### Tool integration

```python
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))
from bg import setup_bg
from loglib import get_logger

setup_bg()  # intercepts --bg, --status, --stop, --tail
log = get_logger("guidelines-generator")
```

### Agent

Uses `tui_default` (or configurable via `--agent`). No dedicated agent needed — the extraction prompt is self-contained in the task template. The agent just needs to read files and follow instructions.

Model: `claude-opus-4.6` by default (same as legacy script — quality matters for pattern extraction).

## What guidelines-generator is NOT

- **Not a linter** — doesn't enforce rules, extracts them
- **Not a style guide writer** — extracts patterns from real code, doesn't invent them
- **Not a one-shot tool** — designed to re-run as code evolves
- **Not repo-specific** — works on any frontend repo with committed files
- **Not a replacement for human review** — generates draft guidelines, humans refine

## Open Questions

- [ ] Should it detect and skip files that haven't changed since last run (incremental mode)?
- [ ] Should phase 2 (review) also use autobuild for consistency?
- [ ] How to handle conflicting patterns between repos (b2c vs white-label)?
- [ ] Should `--to-skills` be automatic or always explicit?
- [ ] Should it generate a PR with the guidelines, or just write locally?
- [ ] Max file size for extraction? Some files are 500+ lines — truncate or split?
