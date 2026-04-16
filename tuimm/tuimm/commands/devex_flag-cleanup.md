---
name: devex_flag-cleanup
description: "Detect stale feature flags and generate cleanup plan. Use when: user says 'flag cleanup', 'stale flags', or 'feature flags'."
---

# Command: $devex_flag-cleanup

Detect stale flags, 100% rollout flags still in code, orphan flags. Generate cleanup plan.

## Services

Ask the user which project to analyze. If not specified, ask before proceeding.

## Process

### 1. List All Flags

Delegate to tuimm_subagent_configcat:
- List all feature flags with: key, last toggle date, rollout percentage per environment, creation date

### 2. Detect Stale Flags

Flags enabled for 3+ months with no toggle activity:
- Flag key, creation date, last toggle date, age
- Current rollout % per environment

### 3. Detect 100% Rollout Flags

Flags at 100% in production — cleanup candidates:
- Flag key, date reached 100%, age at 100%

### 4. Codebase Cross-Reference

Scan codebase for flag usage (grep for flag keys in `.vue`, `.ts`, `.js` files):
- For each flag: list files where it's used
- Detect orphan flags:
  - In ConfigCat but NOT in code → can be deleted from ConfigCat
  - In code but NOT in ConfigCat → dead code referencing removed flag

### 5. Output

Present results using the devex-flag-cleanup template. Follow it EXACTLY.

### 6. Ask User

- "Want me to create Jira cleanup tickets for these?"
- Group by priority: orphans first, then 100% rollout, then stale

NEVER delete flags or create tickets without explicit user confirmation.
