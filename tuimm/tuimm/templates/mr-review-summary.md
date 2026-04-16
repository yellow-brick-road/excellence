---
name: mr-review-summary
description: "MR review summary format. Use when: presenting review results after $mr_review. Contains: header, findings table, quality gate, recommendation, next steps."
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

| # | Severity | File | Line | Issue | Suggestion |
|---|----------|------|------|-------|------------|
| 1 | CRITICAL | {file} | {line} | {issue} | {suggestion} |
| 2 | HIGH | {file} | {line} | {issue} | {suggestion} |

## Security

| # | Type | Scope | Severity | Detail |
|---|------|-------|----------|--------|
| 1 | SAST | 🆕 NEW | CRITICAL | {file}:{line} — {rule}: {description} |
| 2 | SBOM | 🏭 prod | HIGH | {package}@{version} — {CVE-ID}: {description} |

## Quality Gate

| Check | Status |
|-------|--------|
| Pipeline | {✅ passed / ❌ failed / ⏳ running} |
| SonarQube | {✅ passed / ❌ failed / ⚠️ unavailable} |
| Lint | {✅ / ❌} |
| Types | {✅ / ❌} |

## Stats

- Files reviewed: {X}
- Files with issues: {Y}
- Total findings: {Z} ({N} critical, {N} high, {N} medium, {N} low)

## Next Steps

{Actionable recommendations for the MR author. What to fix, what to consider, what's optional.}

Omit sections with no content (e.g. no findings → skip the table). Omit ticket line if no linked ticket. Omit feature branch URL if target is not a feature branch.

RULES: This is the COMPLETE output. Do NOT add commentary, follow-up questions, or recommendations beyond the Next Steps section. Do NOT add sections not defined above.
