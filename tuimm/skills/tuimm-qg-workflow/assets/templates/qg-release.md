---
name: qg-release
description: "Release proposal for $qg_release. Use when: presenting version bump and changelog."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Release Proposal — {package}
   Current: {current_version}
   Proposed: {new_version} ({major/minor/patch})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason: {what triggered the classification}

## [{new_version}] — {DATE}

### ⚠️ Breaking Changes
- {description} (!{iid}, {TICKET-ID})

### ✨ Features
- {description} (!{iid}, {TICKET-ID})

### 🐛 Fixes
- {description} (!{iid}, {TICKET-ID})

### 🏗️ Internal
- {description} (!{iid})

MRs included: {count}
Tickets referenced: {list}

RULES: Omit empty changelog sections. This is the COMPLETE output. Do NOT add commentary or follow-up questions. Wait for user approval.
