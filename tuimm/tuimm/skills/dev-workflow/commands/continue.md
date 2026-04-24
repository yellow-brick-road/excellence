---
name: dev_continue
description: "Resume interrupted workflow. Use when: user says 'continue' or 'resume'."
---

# Command: $dev_continue

Resume an interrupted solve or implement workflow.

## Process

1. Find existing workspace — scan `~/.kiro/temp/dev/` for directories. List them and ask user which one to resume if multiple exist
2. `cd` into the workspace. Check git status — what branch, what's staged/unstaged?
3. If a Jira ticket is associated (extract from dir name or branch), gather full context following the jira-context-gathering skill
4. Determine where we left off in the $dev_solve or $dev_implement flow
5. Present current state to user and ask how to proceed

Present status using the dev-continue template. Follow it EXACTLY — LAST STEP, nothing after this.
