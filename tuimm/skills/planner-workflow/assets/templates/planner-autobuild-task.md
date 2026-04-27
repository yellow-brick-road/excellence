# Autobuild Task Template

Use this template when generating task files for `$planner_autobuild`. Each task file is a self-contained mission brief — the spawned agent has NO prior context. Everything it needs must be in the file or referenced explicitly.

## Frontmatter

```yaml
---
deps: ["01", "03"]              # task IDs that must complete first (empty = no deps)
gate: false                      # true = pipeline stops if this fails
timeout: 300                     # seconds (120=short, 300=standard, 600=heavy, 900+=very heavy)
creates: ["path/to/output.md"]   # files that must exist after execution (verification)
---
```

## Body structure

```markdown
# [Task title — descriptive, unique]

## Tu misión
[1-2 sentences: what to produce, how long, what format. Be specific.]

## Proceso

### 1. INVESTIGAR (do this BEFORE writing anything)

**Knowledge base searches:**
- Search KB "[name]" for: "[query]"
- Search KB "[name]" for: "[query]"

**Files to read:**
- `path/to/source-file.ts` — [why: the code to test / the file to migrate / etc.]
- `path/to/reference.spec.ts` — [why: style reference for output format]
- `path/to/config.ts` — [why: understand project setup]

**Web searches (only if needed):**
- "[specific query]" — [why: need external data not in KBs]

### 2. EJECUTAR

**Output:** `path/to/output-file.ext`

**Content requirements:**
- [Specific requirement 1]
- [Specific requirement 2]
- [Format: bullet points / prose / code / etc.]
- [Length: approximate]

**Constraints:**
- [Domain-specific constraint 1]
- [Domain-specific constraint 2]

### 3. AUTO-REVISAR (max 2 iterations)

Review your output against this checklist. Fix issues and re-review ONCE. After 2 iterations, output what you have — do not loop forever.

- [ ] [Check 1 — e.g., "Every data point has a source (file path or KB result)"]
- [ ] [Check 2 — e.g., "Tests verify behavior, not implementation"]
- [ ] [Check 3 — e.g., "Output file matches the required format"]
- [ ] [Check 4 — e.g., "No hardcoded values that should be configurable"]
- [ ] [Check 5 — domain-specific check]

### 4. NOTAS DE CAMBIOS

After completing, write a brief log:
- What you produced
- Key decisions made and why
- Issues found that couldn't be resolved (for human review)
- Sources consulted (KB results, files read, web searches)
```

## Rules for task generation

1. **Self-contained** — the agent gets NO context from previous tasks or the parent session. Everything goes in the file.
2. **Investigate first** — always read sources BEFORE producing output. No hallucination from memory.
3. **Bounded review** — max 2 iterations. Prevents infinite loops that eat the timeout.
4. **Verifiable** — the `creates` field lets autobuild confirm output exists.
5. **Traceable** — the notes section logs decisions and sources for human review.
6. **No shared files** — each task writes to its OWN output file. Never append to a file another parallel task might touch.
7. **Sources required** — every claim, data point, or decision in the output must reference where it came from (file path, KB search result, web source).
