---
name: mr_list
description: "Cross-repo MR briefing. Use when: user says 'list', 'my MRs', or 'MR briefing'."
---

# Command: $mr_list

Action-oriented MR summary across all repos: what needs your attention RIGHT NOW.

## Process

### 1. Detect User

```bash
git config --global user.email
```

Extract username from email.

### 2. Query MRs

Fetch open MRs across all repos via tuimm_subagent_gitlab. For each MR get: iid, title, author, project_path, draft status, pipeline status, approvals.

### 3. Classify

For each MR, determine the user's relationship:
- **Author is bot** (renovate, dependabot, onesource, snyk) → Bot MR
- **Assigned to me** → My MR (check approvals, status)
- **Assigned to someone else** → Review candidate

### 4. Check Interaction Status

For MRs the user has interacted with (approved, commented), check discussions:
- 🔄 RESET — user was in approved_by but approval was reset (new commits)
- 💬 REPLIED — someone replied to user's comment
- ✅ RESOLVED — thread user opened is resolved
- ⏳ WAITING — no new activity since user's last action
- 🆕 NEW — never reviewed

### 5. Output

Present results using the mr-list-summary template. Follow it EXACTLY — LAST STEP, nothing after this.
