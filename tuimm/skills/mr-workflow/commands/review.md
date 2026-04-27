---
name: mr_review
description: "Full MR review with structured feedback. Use when: user says 'review [MR-ID]' or 'review mr [MR-ID]'."
---

# Command: $mr_review

Full MR review with structured feedback and severity levels.

## Process

### 1. Get MR Context

- Fetch MR info via tuimm_subagent_gitlab: title, description, source/target branches, changed files, pipeline status
- If MR has a linked Jira ticket, fetch ticket context via tuimm_subagent_jira: requirements, acceptance criteria

### 2. Ensure Local Repo Access

Clone or reuse workspace at `~/.kiro/temp/mr/mr-{iid}-{repo_name}/` (see GIT.md § Workspace Conventions).

- If dir exists: `cd {dir} && git fetch --all --prune && git checkout {source_branch} && git pull`
- If not: `mkdir -p ~/.kiro/temp/mr && git clone git@ssh.source.tui:{project_path}.git ~/.kiro/temp/mr/mr-{iid}-{repo_name} && cd` into it and checkout source branch

Do NOT delete after review — mr_comments may reuse it.

### 3. Get Full Diff

- Fetch MR diff via tuimm_subagent_gitlab

### 4. Global Analysis

- Does the MR solve the problem described in the ticket/description?
- Are acceptance criteria covered?
- Any breaking changes?
- MR size — warn if too large, suggest splitting

### 5. File-by-File Review

For each changed file, read the FULL file content (not just diff):
- Logic correctness
- Error handling
- Type safety
- Security issues
- Performance concerns
- Accessibility
- Naming and style conventions (check loaded skills)
- Dead code, unused imports

### 6. Security Scan

Follow the security-preflight skill to extract findings from the MR pipeline.
The skill needs the MR diff (from Step 3) to classify SAST findings as NEW vs PREEXISTING.
Include findings in the review summary (Security section).

If no `preflight-sast` job in the pipeline: skip silently. Do not mention it.

### 7. Quality Gate

- Check SonarQube quality gate via tuimm_subagent_sonar (if project key known)
- Feature branch URL for manual testing: `https://tuimusement-{BRANCH}.dev.musement.com` (replace `/` with `-` in branch name)

### 8. Summary

Present results using the mr-review-summary template. Follow it EXACTLY.

### 9. Ask User

Ask user if they want to:
- Post comments on the MR
- Approve the MR
- Do nothing

NEVER post comments without explicit user approval.
