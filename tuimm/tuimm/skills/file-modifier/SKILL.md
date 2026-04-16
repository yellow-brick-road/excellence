---
name: file-modifier
description: |
  File modification conventions for TUI Musement frontend projects.
  Use when: creating or editing files, running lint/format after changes, or batch-modifying multiple files.
  Contains: write tool rules, lint/format execution order, error handling, batch operations, type checking.
---

# File Modification Conventions

Guidelines for modifying files in TUI Musement frontend projects. Follow these whenever creating or editing files.

## Use when

Modifying any file in a project — code, config, docs. Applies to all agents with write access.

## Rules

### 1. Use the write tool

Always use the `write` tool (str_replace, create, insert, append) to modify files. Never use shell commands like `sed`, `awk`, or `echo >>` for file modifications — they're error-prone and hard to verify.

### 2. Lint after modifying

After modifying `.ts`, `.js`, `.vue`, `.scss`, `.css` files, run lint fix:

```bash
npx eslint --fix {file_path}
```

If the project uses Stylelint (check for `.stylelintrc*` or `stylelint` in package.json):
```bash
npx stylelint --fix {file_path}    # for .scss/.css/.vue files
```

### 3. Format after modifying

After lint fix, run Prettier if the project uses it (check for `.prettierrc*` or `prettier` in package.json):

```bash
npx prettier --write {file_path}
```

### 4. Order matters

1. Write changes
2. ESLint --fix
3. Stylelint --fix (if applicable)
4. Prettier --write (if applicable)

Running in this order prevents conflicts between tools.

### 5. Handle lint errors

If lint fix reports errors it can't auto-fix:
- Read the error output
- Fix the issue in the file
- Re-run lint fix
- Max 2 retries — if still failing, report to parent agent

### 6. Check project setup first

Before running lint/format, verify the project has the tools:
- `grep -q eslint package.json` — if not found, skip ESLint
- `grep -q prettier package.json` — if not found, skip Prettier
- `grep -q stylelint package.json` — if not found, skip Stylelint

### 7. Batch modifications

When modifying multiple files in the same commit:
- Make all file changes first
- Run lint/format once at the end on all changed files:
  ```bash
  npx eslint --fix {file1} {file2} {file3}
  npx prettier --write {file1} {file2} {file3}
  ```

### 8. Type checking

After modifying `.ts` or `.vue` files, run type check if available:
```bash
npx vue-tsc --noEmit    # Vue/Nuxt projects
npx tsc --noEmit        # Pure TypeScript projects
```

Type errors are blocking — fix them before proceeding.

### 9. New files

When creating new files:
- Follow project naming conventions (check CONVENTIONS steering)
- Add to the correct directory based on file type
- Include necessary imports
- Run lint/format after creation

### 10. Deleted files

When deleting files:
- Check for imports referencing the deleted file (grep for the filename)
- Update or remove those imports
- Run lint/format on files that had imports updated
