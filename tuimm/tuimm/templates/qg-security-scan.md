---
name: qg-security-scan
description: "Security scan output for $qg_security-scan and $mr_review security step. Use when: presenting preflight-sast findings."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 Security Scan — !{IID} {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 {project_path} · {source_branch} → {target_branch}
🔗 {mr_url}
⚙️ Pipeline: {pipeline_id} · Job: preflight-sast ({job_status})

🎯 Verdict: {🟢 PASS | 🟡 REVIEW NEEDED | 🔴 BLOCK}

## SAST Findings

| # | Scope | Severity | File | Line | Rule | Description |
|---|-------|----------|------|------|------|-------------|
| 1 | 🆕 NEW | CRITICAL | {file} | {line} | {rule} | {description} |
| 2 | 📦 PRE | HIGH | {file} | {line} | {rule} | {description} |

## SBOM Findings — Critical / High

| # | Scope | Package | Version | Advisory | Description |
|---|-------|---------|---------|----------|-------------|
| 1 | 🏭 prod | {pkg} | {ver} | {CVE-ID} | {description} |
| 2 | 🔧 dev | {pkg} | {ver} | {CVE-ID} | {description} |

## SBOM Findings — Medium / Low

| # | Scope | Package | Version | Advisory | Description |
|---|-------|---------|---------|----------|-------------|
| 1 | 🏭 prod | {pkg} | {ver} | {CVE-ID} | {description} |

## Summary

- SAST: {N} new (introduced by MR), {N} preexisting
- SBOM: {N} critical, {N} high, {N} medium, {N} low ({N} in prod deps)
- Actionable: {what blocks or needs attention}
- Preexisting debt: {what was already there — informational, not blocking}

RULES: This is the COMPLETE output. Omit sections with zero findings. Scope column: 🆕 NEW for MR-introduced, 📦 PRE for preexisting (SAST); 🏭 prod or 🔧 dev for dependency scope (SBOM). Do NOT add commentary, recommendations, or follow-up questions after the Summary.
