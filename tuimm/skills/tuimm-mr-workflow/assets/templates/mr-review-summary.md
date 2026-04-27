---
name: mr-review-summary
description: "MR review summary format. Use when: presenting review results after $mr_review. Contains: header, findings with code, quality gate, recommendation, next steps."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 MR Review — !{IID} {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 {project_path} · {source_branch} → {target_branch}
🎫 {TICKET-ID}: {ticket_title}
🔗 {mr_url}
🌐 {feature_branch_url}

🎯 Recommendation: {🟢 APPROVE | 🟡 APPROVE WITH COMMENTS | 🟠 REQUEST CHANGES | 🔴 BLOCK}

{One-paragraph summary of what the MR does and the overall assessment.}

## Findings

### #{N} [{CRITICAL|HIGH|MEDIUM|LOW}] {Short title of the issue}

📄 `{file}` · L{line}

**Problem:** {What's wrong and why it matters — concrete, not vague.}

```{lang}
// Current code (what the MR has)
{relevant snippet showing the problem}
```

**Fix:** {What to do and why.}

```{lang}
// Proposed change
{concrete code showing the fix}
```

---

{Repeat for each finding, separated by ---. Order by severity: CRITICAL → HIGH → MEDIUM → LOW.}

## Security

- [{CRITICAL|HIGH|MEDIUM|LOW}] **{SAST|SBOM|SECRET}** {🆕 NEW | 📦 PRE} — `{file}:{line}` — {rule}: {description}. {Action needed or "Not introduced by this MR."}

## Quality Gate

- Pipeline: {✅ passed | ❌ failed | ⏳ running | ⚠️ details}
- SonarQube: {✅ passed | ❌ failed | ⚠️ details}
- Preflight SAST: {✅ 0 new | ❌ N new findings}
- Approvals: {✅ N/M (names) | ❌ N/M}

## Stats

- Files reviewed: {X} · With issues: {Y}
- Findings: {Z} ({N} critical, {N} high, {N} medium, {N} low)

## Next Steps

{Actionable list — what to fix, what's optional, what's blocking.}

---

Omit sections with no content (e.g. no findings → skip entirely). Omit ticket line if no linked ticket. Omit feature branch URL if target is not a feature branch. Security section: use bullet list, one line per finding.

RULES: This is the COMPLETE output. Do NOT add commentary, follow-up questions, or recommendations beyond the Next Steps section. Do NOT add sections not defined above.
