---
name: qg_generate-guidelines
description: "Extract coding guidelines from a project's real code. Use when: user says 'generate guidelines', 'extract guidelines', 'coding standards from code'."
---

# Command: $qg_generate-guidelines

Extract coding guidelines from a project's existing codebase using the guidelines-generator tool.

## Critical: how the tool works

- The tool uses the CURRENT WORKING DIRECTORY as the project root (git root detection)
- `--dir` is NOT the project path — it's a filter for subdirectories within the project. Do NOT use it to specify the project
- `--bg` does NOT propagate other flags — the subprocess runs from CWD with only `--phase`
- `--scan` MUST run before `--phase` — without it, the database doesn't exist and extraction fails

## NEVER do these

- NEVER use `sleep` to wait for progress — it blocks the conversation
- NEVER use `--tail` — it blocks waiting for streaming output
- NEVER pass `--dir <project-path>` thinking it sets the project root
- NEVER launch `--phase` without running `--scan` first

## Process

### 1. Ensure correct CWD

The user must be in the project directory. Check with `pwd`. If the CWD is not the target project, tell the user to cd there first, or use `cd <project> &&` before commands.

### 2. Detect file extensions

Before scanning, check what source files exist in the repo:

```bash
cd <project> && git ls-files --cached | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

Based on the result, determine the right `--extensions` regex:
- Frontend (vue/ts/js): `\.(vue|ts|js|tsx|jsx)$` (default, no flag needed)
- Java: `\.java$`
- Python: `\.(py|pyi)$`
- Go: `\.go$`
- Mixed: combine as needed, e.g. `\.(java|xml)$`

### 3. Scan (synchronous, fast)

```bash
cd <project> && python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --scan [--extensions 'REGEX']
```

Show the scan results (categories, file counts, LOC). If 0 files, wrong directory.

### 4. Confirm and launch

Show the user what was found. Ask for confirmation. Once confirmed:

```bash
cd <project> && python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --phase all --bg [--extensions 'REGEX']
```

Options the user might want:
- `--workers N` — parallel workers (default: 3)
- `--max-tasks N` — limit extraction tasks
- `--agent NAME` — override agent (default: tuimm_default)
- `--only CATEGORY` — filter categories (comma-separated)

### 5. Return control immediately

Show the run UID. Tell the user how to check progress. Return control — do NOT wait.

When the user asks for progress ("report", "cómo va", "status"):

```bash
cd <project> && python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py --report
```

### 6. Output

When complete, present results using the qg-generate-guidelines template. Follow it EXACTLY — LAST STEP, nothing after this.

Output: `docs/guidelines/` in the project root, one markdown file per category.
Copy to skills: add `--to-skills` flag.
