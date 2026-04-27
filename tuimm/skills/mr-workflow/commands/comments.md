---
name: mr_comments
description: "Address review comments on your MR. Use when: user says 'comments [MR-ID]' or MR is assigned to user."
---

# Command: $mr_comments

Address review comments on your own MR — analyze each one, recommend action, apply fixes.

## Process

### 1. Get MR Context

- Fetch MR info + all discussions via tuimm-subagent_gitlab
- Get ticket context via tuimm-subagent_jira if linked (follow jira-context-gathering skill)
- Clone or reuse workspace at `~/.kiro/temp/mr/mr-{iid}-{repo_name}/` (see GIT.md § Workspace Conventions). If dir exists: fetch + checkout. If not: clone + checkout MR source branch
- Count unresolved threads. If zero: "No unresolved comments. Nothing to do."

### 2. For Each Unresolved Comment

**Before presenting: investigate.**

1. Read the FULL file being discussed — not just the diff line, the whole file (or at minimum 50 lines above and below). You need surrounding context to judge the comment
2. Understand what the code does and WHY it was written this way. Check: is there a pattern in the file? Is this intentional? Does the ticket/AC explain the choice?
3. If the comment references a concept (race condition, fallback, loading state), verify whether the concern actually applies to this code path
4. For bot comments: bots flag patterns mechanically. Check if the suggestion makes sense given the actual implementation. Common false positives: suggesting fallbacks for values that are guaranteed by the component lifecycle, flagging optional chaining where the value is always defined, suggesting error handling where the parent already handles it
5. Form your assessment: Is this valid? Partially valid? A false positive? A style preference vs a real bug?

**Then present using the mr-comment-item template. Follow it EXACTLY — field by field, line by line.**

Wait for user action before proceeding to next comment.

### 3. Apply Changes

When applying code changes:
1. Show proposed change with context, ask confirmation
2. Apply change
3. Run quality checks (lint, types)
4. Commit via tuimm-subagent_gitlab (follow commit-conventions skill)
5. Mark comment as resolved via tuimm-subagent_gitlab

### 4. Response Tone

**For BOT comments:** Brief, direct
- "Not applicable — by design"
- "False positive — handled elsewhere"
- "Keeping current implementation — [reason]"

**For HUMAN comments:** Friendly, collaborative
- "Good catch! Fixed"
- "Makes sense, updated"
- "You're right, adding the check"

### 5. Final Summary

Present final summary using the mr-comments-summary template. Follow it EXACTLY — LAST STEP, nothing after this.

User must push manually.
