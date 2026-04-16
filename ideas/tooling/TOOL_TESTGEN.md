# Tool: test-generator

Test generation pipeline for frontend repositories. Scans a codebase, classifies files by type, identifies testing gaps, and generates unit tests via AI agents through autobuild.

## What it is

A CLI tool that takes a Vue/Nuxt frontend repo and generates missing unit tests for every file that needs them. Uses the Testing Philosophy file-type matrix to decide **what** to test per file, and AI agents with testing skills to generate the actual test code.

Not a test runner. Not a coverage tool. A **test writer** that fills gaps in existing repos.

### The problem it solves

Product teams have repos with 40-60% coverage. Nobody writes tests for existing code voluntarily. The gap grows with every sprint. Excellence can't mandate "write more tests" — that's noise. But Excellence CAN offer: "run this tool and get tests for everything that's missing."

### Core principle: test intent, not implementation

> A test that asserts buggy behavior is worse than no test.

The test-generator does NOT just mirror what the code currently does. For each generated test, the agent must verify:
1. What is the test checking?
2. Is this the CORRECT expected behavior, or just mirroring implementation?
3. Any edge cases or intent mismatches?

Red flags the agent must avoid:
- Tests that would pass even if the feature was broken
- Assertions too loose to catch regressions
- Mocks hiding real bugs
- Untested state transitions or data transformations

### Connection to Excellence

- Implements Testing Philosophy (the file-type matrix becomes the scanner's brain)
- Uses autobuild as execution engine (tasks, waves, verify, retry)
- Distributed via TUI CLI (`tui fe test-gen`)
- Dedicated `excellence_test-generator` agent with testing-only skills
- Coverage delta is a measurable KPI for Excellence reporting

## Dependencies

| Tool | Why |
|------|-----|
| autobuild | Task execution engine (waves, verify, retry, progress) |
| bg | Background execution (`--bg/--status/--stop`) |
| logd | Structured logging |
| kiro-cli | ACP backend for agent execution |
| excellence_test-generator | Specialized agent for test generation (see below) |

Also requires the target repo to have vitest configured.

## File layout

```
~/.kiro/tools/test-generator/
  testgen.py                    # CLI entry point + scanner + planner + reporter
  __tests__/                    # Unit tests

~/.kiro/templates/test-generator/
  nuxt-component.md             # Interactive Vue/Nuxt components
  nuxt-composable.md            # Composables
  nuxt-store.md                 # Pinia stores
  nuxt-utility.md               # Pure functions / helpers
  nuxt-middleware.md             # Nuxt middleware
  nuxt-api-layer.md             # API / service layers
  nuxt-plugin.md                # Nuxt plugins (server/client)

~/.kiro/skills/
  excellence_testing/SKILL.md                  # Generic: philosophy, anti-patterns, what NOT to test
  excellence_testing-nuxt-component/SKILL.md   # How to test Vue/Nuxt components
  excellence_testing-nuxt-composable/SKILL.md  # How to test composables
  excellence_testing-nuxt-store/SKILL.md       # How to test Pinia stores
  excellence_testing-nuxt-utility/SKILL.md     # How to test utilities
  excellence_testing-nuxt-middleware/SKILL.md   # How to test middleware
  excellence_testing-nuxt-api-layer/SKILL.md   # How to test API layers
  excellence_testing-nuxt-plugin/SKILL.md      # How to test plugins
  excellence_test-generator/SKILL.md           # CLI reference for the tool

~/.kiro/agents/
  excellence_test-generator.json               # Dedicated test writing agent
```

Installed via `tui ai install tools test-generator` (resolves deps: logd → bg → autobuild → test-generator + agent).

### Naming convention

All artifacts follow `{framework}-{type}` pattern:
- Templates: `nuxt-component.md`, `nuxt-composable.md`, ...
- Skills: `excellence_testing-nuxt-component`, `excellence_testing-nuxt-composable`, ...

Future React Native support: `rn-component.md`, `excellence_testing-rn-hook`, etc.

## Agent: excellence_test-generator

A dedicated kiro-cli agent purpose-built for writing unit tests. Not a general-purpose agent — it only knows how to read source code and produce test files.

### Why a dedicated agent

A general-purpose agent (tui_default) has too much context: Jira skills, GitLab skills, MR review templates, commit conventions. All noise when the task is "read this composable, write tests." A focused agent:
- Loads only testing-relevant skills → smaller context, better output
- Has a system prompt tuned for test writing → no ambiguity about what to produce
- Can be optimized independently (model, temperature, token limits)
- Can be shared across the org without exposing other capabilities

### Agent config

```json
{
  "name": "excellence_test-generator",
  "description": "Specialized agent for generating unit tests for Vue/Nuxt frontend repos using Vitest",
  "model": "claude-sonnet-4.6",
  "resources": [
    "skill://vitest",
    "skill://tui_vitest_plan",
    "skill://vue",
    "skill://vue-best-practices",
    "skill://nuxt",
    "skill://tui_vue-component-guidelines",
    "skill://excellence_testing",
    "skill://excellence_testing-nuxt-component",
    "skill://excellence_testing-nuxt-composable",
    "skill://excellence_testing-nuxt-store",
    "skill://excellence_testing-nuxt-utility",
    "skill://excellence_testing-nuxt-middleware",
    "skill://excellence_testing-nuxt-api-layer",
    "skill://excellence_testing-nuxt-plugin"
  ],
  "tools": ["fs_read", "fs_write", "execute_bash", "glob", "grep", "code"],
  "allowedTools": ["fs_read", "fs_write", "execute_bash", "glob", "grep", "code"]
}
```

No MCP servers. No Jira, GitLab, Datadog, Confluence. Just file tools + testing skills.

### System prompt

```
You are a specialized test writer for Vue/Nuxt frontend projects using Vitest.

Your ONLY job is to generate high-quality unit tests. You receive a source file
with its type classification and testing strategy. You produce a .spec.ts file.

Rules:
- Write ONLY the test file. No explanations, no commentary, no markdown.
- Test INTENDED BEHAVIOR, not current implementation. Never just mirror what the code does.
- For each test, verify: is this the CORRECT expected behavior, or just what the code
  currently returns? If the code has a bug, the test must NOT assert the buggy behavior.
- Watch for: tests that would pass even if the feature was broken, assertions too loose
  to catch regressions, mocks that hide real bugs, edge cases not covered.
- Follow the testing strategy from the corresponding excellence_testing-nuxt-* skill.
- Use the style reference from the repo for consistency.
- Arrange / Act / Assert pattern in every test.
- Group tests by behavior (describe blocks), not by method name.
- Mock at boundaries only (API calls, external services).
- DO NOT use snapshot tests.
- DO NOT test framework internals.
- If the file is too complex to test in isolation, focus on the public API
  and note untestable areas in a comment.

Environment:
- Vitest 3.x + @nuxt/test-utils
- Environment: nuxt (auto-imports available)
- DO NOT mock: useRoute, useRouter, useState, useFetch
- Use mountSuspended for async components
- Use createPinia() + setActivePinia() for store tests
```

### Skills architecture

Testing knowledge is split into skills, not embedded in templates or steering files:

**Generic skill (`excellence_testing`):**
- Testing philosophy: behavior over coverage
- What NOT to test (explicit skip list)
- Anti-patterns: snapshot abuse, testing internal state, over-mocking
- Coverage strategy per layer

**Per-file-type skills (`excellence_testing-nuxt-{type}`):**
- What to test for this type
- What NOT to test for this type
- Example test structure (real patterns from TUI repos)
- Environment rules specific to this type
- Common gotchas

Skills are reusable: the test-generator agent loads all of them, but other agents (tui_dev, quality guardian) can load specific ones as needed.

### No MCP needed

The agent doesn't need external tools:
- Reads source files via `fs_read` (provided by kiro-cli)
- Writes test files via `fs_write`
- Runs vitest via `execute_bash` (for verify)
- Searches code via `grep`/`code` (to understand imports and dependencies)

All tools are built into kiro-cli. Zero infrastructure dependency.

### Future: per-file-type agents

v1 uses a single agent for all file types. The task template references the relevant skill.

If quality varies significantly by file type, v2 could split into specialized sub-agents:
- `excellence_test-generator-component` — Vue component testing specialist
- `excellence_test-generator-logic` — composables, stores, utilities specialist

But this is premature optimization. Start with one agent, measure quality per file type, split only if needed.

## Usage

```bash
# From any frontend repo root
testgen                          # scan + generate tasks (dry run)
testgen --run                    # scan + generate + execute via autobuild
testgen --run --bg               # same, in background
testgen --status                 # check autobuild progress
testgen --report                 # coverage delta report

# Filters
testgen --only composables       # only one file type
testgen --only components        # only components
testgen --dir src/features/booking  # only one directory
testgen --file src/composables/useBooking.ts  # single file

# Overrides
testgen --agent tui_default      # override agent
testgen --model claude-sonnet-4.6  # override model
testgen --workers 3              # parallel task execution
testgen --max-tasks 20           # limit number of tasks generated

# Inspection
testgen --scan                   # scan only, print classification table
testgen --plan                   # generate tasks, print plan, don't execute
```

## Architecture

```
testgen.py (single file)
    │
    ├── scan(repo_path) → FileInfo[]
    │     Walk src/, classify each file, detect existing tests
    │
    ├── plan(files, templates) → tasks/
    │     Generate autobuild task .md files for untested files
    │     Load templates from ~/.kiro/templates/test-generator/
    │     Generate autobuild.json config
    │
    ├── run(tasks_dir)
    │     Delegate to autobuild (subprocess or direct import)
    │
    └── report(build_dir, repo_path)
          Parse autobuild results, compute coverage delta
```

testgen is NOT an engine. It's a **task generator** that feeds autobuild. The execution, retry, progress, and verification are all autobuild's job.

## Scanner

### File classification

The scanner walks the repo and classifies each `.vue` and `.ts` file. Classification is deterministic — no AI needed.

```python
@dataclass
class FileInfo:
    path: Path              # relative to repo root
    file_type: str          # classification (see below)
    has_test: bool          # corresponding .spec.ts exists
    test_path: Path | None  # path to existing test (if any)
    loc: int                # lines of code (excluding blanks/comments)
    complexity: str         # low/medium/high (heuristic)
    skip_reason: str        # why skipped (if applicable)
```

### Classification rules

| Pattern | Classification | Template | Test? |
|---------|---------------|----------|-------|
| `components/**/*.vue` with interaction markers | `nuxt-component` | `nuxt-component.md` | Yes |
| `components/**/*.vue` without interaction events | `nuxt-component-presentational` | Skip | Skip (unless complex `v-if` chains) |
| `composables/use*.ts` or `**/use*.ts` (not in components/) | `nuxt-composable` | `nuxt-composable.md` | Yes |
| `stores/*.store.ts` or `stores/*.ts` with `defineStore` | `nuxt-store` | `nuxt-store.md` | Yes |
| `utils/**/*.ts` or `helpers/**/*.ts` | `nuxt-utility` | `nuxt-utility.md` | Yes — TDD priority |
| `pages/**/*.vue` | `nuxt-page` | Skip | Skip (integration level) |
| `middleware/**/*.ts` | `nuxt-middleware` | `nuxt-middleware.md` | Yes if branching logic |
| `api/**/*.ts` or `services/**/*.ts` or `**/api.ts` | `nuxt-api-layer` | `nuxt-api-layer.md` | Yes |
| `plugins/**/*.ts` | `nuxt-plugin` | `nuxt-plugin.md` | Case by case |
| `types/**/*.ts` or `*.d.ts` | `type-only` | Skip | Skip |
| `config/**/*.ts` or `*.config.ts` | `config` | Skip | Skip |
| `layouts/**/*.vue` | `layout` | Skip | Skip |
| `assets/**` | `asset` | Skip | Skip |

### Interaction detection (components)

Heuristic scan of `.vue` template section:

```python
INTERACTION_MARKERS = [
    r'@click', r'@input', r'@submit', r'@change', r'@keydown',
    r'@keyup', r'@focus', r'@blur', r'@mouseenter', r'@mouseleave',
    r'v-model', r'@update:', r'defineEmits',
]
```

If any marker is found in the file → `nuxt-component`. Otherwise → `nuxt-component-presentational`.

### Presentational complexity check

Presentational components are skipped UNLESS they have complex conditional rendering:

```python
COMPLEX_MARKERS = [
    r'v-if.*v-else-if',     # chained conditionals
    r'v-for.*v-if',          # combined iteration + condition
    r'\?.*\?.*:',            # nested ternaries in template
]
```

If complex markers found → reclassify as `nuxt-component` (needs tests).

### Test detection

For each source file, check if a test exists:

```python
def find_test(source: Path, repo_root: Path) -> Path | None:
    stem = source.stem  # e.g., "useBooking" or "SearchButton"
    candidates = [
        source.parent / f"{stem}.spec.ts",                    # colocated
        source.parent / f"__tests__/{stem}.spec.ts",          # __tests__ folder
        source.parent / f"{stem}.test.ts",                    # .test.ts variant
        source.parent / f"__tests__/{stem}.test.ts",
    ]
    # For .vue files, also check kebab-case
    if source.suffix == ".vue":
        kebab = to_kebab(stem)
        candidates += [
            source.parent / f"{kebab}.spec.ts",
            source.parent / f"__tests__/{kebab}.spec.ts",
        ]
    return next((c for c in candidates if c.exists()), None)
```

### Complexity heuristic

Simple LOC-based heuristic for prioritization:

| LOC | Complexity |
|-----|-----------|
| < 30 | low |
| 30-100 | medium |
| > 100 | high |

High-complexity files get higher priority in the task queue.

### Skip reasons

Files are skipped with an explicit reason:

| Reason | When |
|--------|------|
| `has_test` | Test file already exists |
| `presentational` | Presentational component, no complex logic |
| `type_only` | Type definitions, no runtime code |
| `config` | Configuration file |
| `page` | Page-level (integration, not unit) |
| `layout` | Layout component (structural) |
| `asset` | Non-code asset |
| `too_small` | < 5 LOC (trivial) |
| `generated` | Auto-generated file (detected by header comment) |

## Task Generation

### Output structure

testgen generates a temporary folder that autobuild consumes:

```
.testgen/                          # gitignore this
  autobuild.json                   # autobuild config
  tasks/                           # one .md per file to test
    00_useBooking.md
    01_useSearch.md
    02_SearchButton.md
    03_booking.store.md
    04_formatPrice.md
    ...
  scan-results.json                # full scan output for reporting
```

### autobuild.json

```json
{
  "agent": "excellence_test-generator",
  "model": "claude-sonnet-4.6",
  "review": "none",
  "max_retries": 2,
  "timeout": 120,
  "parallel": {
    "max_workers": 3
  },
  "health": {
    "builtin": true,
    "checks": [
      {
        "name": "vitest",
        "cmd": "npx vitest --version",
        "required": true
      },
      {
        "name": "node_modules",
        "cmd": "test -d node_modules",
        "required": true
      }
    ]
  }
}
```

Key decisions:
- `agent: "excellence_test-generator"` — dedicated agent with testing skills only, not general-purpose
- `review: "none"` — the verify step (running the test) is sufficient. No need for LLM self-review on test generation
- `max_retries: 2` — if the test doesn't pass, retry with error context. 2 retries is enough; if it can't write a passing test in 3 attempts, it needs human help
- `timeout: 120` — test generation is fast, 2 minutes per file is generous
- `max_workers: 3` — parallel test generation. Each task is independent (different files)

### Task file format

Each task .md follows autobuild's format. The template references the corresponding skill. Example for a composable:

```markdown
---
verify: "npx vitest run src/composables/__tests__/useBooking.spec.ts --reporter=json 2>&1 | tail -1"
creates: ["src/composables/__tests__/useBooking.spec.ts"]
timeout: 120
type: test
---

# Generate unit tests for useBooking.ts

## File type
nuxt-composable

## Source file
Path: `src/composables/useBooking.ts`

\`\`\`typescript
{SOURCE_CONTENT}
\`\`\`

## Testing strategy

Follow `skill://excellence_testing-nuxt-composable` for what to test and what NOT to test.

## Test environment

- Framework: Vitest + @nuxt/test-utils
- Environment: `nuxt` (auto-imports available: ref, computed, useFetch, etc.)
- DO NOT mock: useRoute, useRouter, useState, useFetch (available via nuxt env)
- Use `mountSuspended` for async components
- File convention: `__tests__/{name}.spec.ts`

## Style reference

Follow this existing test pattern from the repo:

\`\`\`typescript
{STYLE_SAMPLE}
\`\`\`

## Rules

- Write ONLY the test file content. No explanations.
- Use `describe` blocks grouped by behavior, not by method name.
- Use `it('should ...')` format.
- Mock external dependencies at the boundary (API calls, external composables).
- DO NOT use snapshot tests.
- DO NOT test internal reactive state — test observable outputs.
- Arrange / Act / Assert pattern in each test.
- Import types from source file when available.
```

### Template variables

Each template receives:

| Variable | Source |
|----------|--------|
| `{SOURCE_CONTENT}` | Full content of the source file |
| `{SOURCE_PATH}` | Relative path to source file |
| `{TEST_PATH}` | Where the test file should be created |
| `{STYLE_SAMPLE}` | Content of an existing .spec.ts from the repo (for style consistency) |
| `{IMPORTS}` | Detected imports from the source file (helps agent understand dependencies) |
| `{ENVIRONMENT}` | Test environment config (nuxt/jsdom/node) |

### Style sampling

testgen picks ONE existing .spec.ts from the repo as a style reference. Selection priority:

1. A test in the same directory as the source file
2. A test for the same file type (e.g., another composable test)
3. Any .spec.ts in the repo
4. Fallback: no style sample (agent uses defaults)

The sample is truncated to 80 lines max to avoid bloating the prompt.

## Templates

Templates live at `~/.kiro/templates/test-generator/` and follow `{framework}-{type}.md` naming.

Each template is lightweight — it provides the autobuild task structure and references the corresponding skill for testing strategy. The knowledge lives in skills, templates are plumbing.

### nuxt-component.md

References `skill://excellence_testing-nuxt-component`. Additional rules:
```
- Use `mountSuspended` from @nuxt/test-utils to mount the component
- Use `wrapper.find()` or `wrapper.get()` to query elements
- Trigger events with `await wrapper.find('button').trigger('click')`
- Check emitted events with `wrapper.emitted('eventName')`
- For v-model: test both prop update and emit
```

### nuxt-composable.md

References `skill://excellence_testing-nuxt-composable`.

### nuxt-store.md

References `skill://excellence_testing-nuxt-store`. Additional rules:
```
- Use `createPinia()` and `setActivePinia()` in beforeEach
- Test actions by calling them and checking state
- Test getters by setting state and checking return values
- For async actions: mock the API layer, test state transitions
```

### nuxt-utility.md

References `skill://excellence_testing-nuxt-utility`. Additional rules:
```
- Environment: node (no DOM needed)
- No mocking needed for pure functions
- Use `describe.each` or `it.each` for parameterized tests
- Test error cases with `expect(() => fn()).toThrow()`
```

### nuxt-middleware.md

References `skill://excellence_testing-nuxt-middleware`.

### nuxt-api-layer.md

References `skill://excellence_testing-nuxt-api-layer`. Additional rules:
```
- Mock the HTTP client (useFetch, $fetch, ofetch)
- Test request construction separately from response handling
- Use vi.fn() for mock responses
```

### nuxt-plugin.md

References `skill://excellence_testing-nuxt-plugin`.

### Future templates

When React Native support is added:
- `rn-component.md` → references `skill://excellence_testing-rn-component`
- `rn-hook.md` → references `skill://excellence_testing-rn-hook`

## Verify Strategy

Each task's `verify` field runs the generated test:

```bash
npx vitest run {TEST_PATH} --reporter=json 2>&1 | tail -1
```

Exit code 0 = tests pass = task succeeds.
Non-zero = tests fail = autobuild retries with error context.

On retry, autobuild includes the error output in the prompt, so the agent can fix the test.

### What verify catches

- Import errors (wrong path, missing export)
- Runtime errors (undefined variables, type mismatches)
- Assertion failures (wrong expected values)
- Environment issues (missing auto-imports, wrong test env)

### What verify doesn't catch

- Shallow tests (tests that pass but don't test anything meaningful)
- Tests coupled to implementation (testing internal state)
- Missing edge cases

These are quality issues, not correctness issues. They're addressed by:
1. The skills (tell agent what to test and what NOT to test)
2. Future: Quality Guardian agent reviews generated tests

## Report

After execution, testgen generates a report:

```
.testgen/report.md
```

Contents:

```markdown
# test-generator Report — 2026-03-26

## Summary
- Files scanned: 142
- Files needing tests: 47
- Files skipped: 95 (38 has_test, 22 presentational, 15 page, 12 type_only, 8 config)
- Tasks generated: 47
- Tasks passed: 41
- Tasks failed: 6
- Coverage before: 43%
- Coverage after: 71%
- Delta: +28%

## Generated tests (41)
| File | Type | Test path | Status |
|------|------|-----------|--------|
| useBooking.ts | nuxt-composable | __tests__/useBooking.spec.ts | ✅ passed |
| useSearch.ts | nuxt-composable | __tests__/useSearch.spec.ts | ✅ passed |
| SearchButton.vue | nuxt-component | __tests__/SearchButton.spec.ts | ✅ passed |
| booking.store.ts | nuxt-store | __tests__/booking.store.spec.ts | ✅ passed |
| formatPrice.ts | nuxt-utility | __tests__/formatPrice.spec.ts | ✅ passed |
| ... | ... | ... | ... |

## Failed (6)
| File | Type | Error | Attempts |
|------|------|-------|----------|
| PaymentForm.vue | nuxt-component | TypeError: Cannot read 'stripe' | 3 |
| useCheckout.ts | nuxt-composable | Mock setup failed | 3 |
| ... | ... | ... | ... |

## Skipped (95)
| File | Type | Reason |
|------|------|--------|
| BaseButton.vue | nuxt-component-presentational | No complex logic |
| BookingPage.vue | nuxt-page | Integration level |
| types/booking.ts | type-only | No runtime code |
| ... | ... | ... |

## File type breakdown
| Type | Total | Tested | Generated | Skipped | Failed |
|------|-------|--------|-----------|---------|--------|
| nuxt-composable | 18 | 8 | 9 | 0 | 1 |
| nuxt-component | 34 | 12 | 18 | 0 | 4 |
| nuxt-component-presentational | 22 | 0 | 0 | 22 | 0 |
| nuxt-store | 6 | 3 | 3 | 0 | 0 |
| nuxt-utility | 12 | 8 | 4 | 0 | 0 |
| nuxt-middleware | 4 | 2 | 1 | 0 | 1 |
| nuxt-api-layer | 8 | 3 | 5 | 0 | 0 |
| nuxt-page | 15 | 0 | 0 | 15 | 0 |
| type-only | 12 | 0 | 0 | 12 | 0 |
| config | 8 | 0 | 0 | 8 | 0 |
| layout | 3 | 0 | 0 | 3 | 0 |
```

### Coverage delta

testgen runs vitest coverage before and after:

```bash
# Before
npx vitest run --coverage --reporter=json > .testgen/coverage-before.json

# After (all tests including generated)
npx vitest run --coverage --reporter=json > .testgen/coverage-after.json
```

The delta is the headline metric for Excellence reporting.

## Edge Cases

### Monorepos (b2c-nuxt-libraries)

testgen detects monorepo structure (npm workspaces, lerna.json, pnpm-workspace.yaml):

```bash
testgen                           # scans all packages
testgen --package @dx/b2c-foundation  # single package
```

Each package gets its own task batch. Vitest verify commands use the package's own config.

### Legacy repos (Nuxt 2, Vue 2)

testgen checks the framework version:
- Nuxt 4 / Vue 3 → `nuxt-*` templates and skills
- Nuxt 2 / Vue 2 → future `nuxt2-*` templates (not in v1)
- Unknown → abort with message

Detection: read `package.json` for `nuxt` and `vue` versions.

### Existing shallow tests

If a test file exists but is shallow (< 3 test cases for a file with > 50 LOC), testgen can optionally regenerate:

```bash
testgen --regenerate-shallow      # replace tests with < 3 cases
```

Default: skip files with existing tests (conservative).

### Files with complex dependencies

Some files import from many internal modules, making them hard to test in isolation. testgen detects high import count (> 10 internal imports) and:
1. Adds a note to the task: "This file has many dependencies. Focus on testing the public API, mock internal imports."
2. Increases timeout to 180s
3. Marks as `complexity: high` in the report

### Generated files

Files with auto-generated headers (`// auto-generated`, `/* eslint-disable */` at top, `.generated.ts`) are skipped.

## CLI Integration

### Standalone

```bash
testgen [options]                  # from repo root
```

### Via TUI CLI (future)

```bash
tui fe test-gen                    # scan + generate
tui fe test-gen --run              # scan + generate + execute
tui fe test-gen --report           # show report
```

`tui fe test-gen` wraps testgen with TUI-specific defaults (agent, model, skills).

## Implementation Notes

### Single file

testgen.py is a single Python file (~400 lines). No external dependencies beyond stdlib. Templates are loaded from `~/.kiro/templates/test-generator/`.

Sections:
1. Scanner (~150 lines) — walk, classify, detect tests
2. Planner (~100 lines) — generate task .md files + autobuild.json
3. Reporter (~80 lines) — parse results, compute delta, generate report
4. CLI (~70 lines) — argparse, dispatch, bg integration

### Why single file

Same pattern as logd.py, bg.py, engine.py. No package management, no imports beyond stdlib, copy-deployable.

### bg integration

testgen uses bg for background execution:

```python
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/bg"))
from bg import setup_bg
setup_bg()  # intercepts --bg, --status, --stop, --tail
```

### logd integration

```python
sys.path.insert(0, os.path.expanduser("~/.kiro/tools/logd"))
from loglib import get_logger
log = get_logger("testgen")
```

Logs: scan results, task generation, autobuild delegation, report generation.

## What testgen is NOT

- **Not a test runner** — vitest runs the tests. testgen generates them
- **Not a coverage tool** — vitest provides coverage. testgen computes the delta
- **Not a replacement for writing tests** — it's a bootstrap. Generates 80%, dev adjusts 20%
- **Not for greenfield** — if you're starting a new project, write tests as you go (TDD). testgen is for existing code with gaps
- **Not for pages** — page-level tests are integration tests, not unit tests. testgen generates unit tests only
- **Not for legacy JS** — TypeScript repos only. Plain JS files are skipped with a warning

## Open Questions

- [ ] Should testgen detect and skip files that are "too coupled" (circular imports, god objects)?
- [ ] Should it generate a PR with all tests, or commit per file type?
- [ ] How to handle files that need specific test setup (Stripe, Google Maps, etc.)?
- [ ] Should the report include test quality metrics (assertion count, branch coverage per test)?
- [ ] How to handle `.vue` files with both `<script setup>` and `<script>` blocks?
- [ ] Should testgen create a `conftest`-equivalent (shared test utilities) if none exists?
- [ ] Rate limiting: how many parallel ACP sessions can kiro-cli handle?
