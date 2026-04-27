# Autobuild Report

## Run summary

| | |
|---|---|
| Goal | [what was the objective] |
| Scope | [what was covered] |
| Tasks | [completed]/[total] |
| Waves | [N] |
| Workers | [N] parallel |
| Duration | [time] |

## Results by wave

| Wave | Tasks | Status |
|------|-------|--------|
| 1 | task-01, task-02, task-03 | ✅ all passed |
| 2 | task-04, task-05 | ✅ passed / ❌ task-05 failed |
| 3 | task-06 [GATE] | ✅ consolidated |

## Output files

| File | Task | Status |
|------|------|--------|
| `path/to/output1.ts` | task-01 | ✅ Created |
| `path/to/output2.ts` | task-02 | ✅ Created |
| `path/to/output3.ts` | task-05 | ❌ Failed — needs manual review |

## Failed tasks (need manual review)

### task-05: [title]
- **Error:** [what went wrong]
- **Attempts:** [N]/[max_retries]
- **Last output:** [partial file path or "none"]
- **Suggested fix:** [what the human should do]

## Cleanup

- [ ] KBs removed: [list]
- [ ] Task files: [kept / removed]
- [ ] Output files: [location]
