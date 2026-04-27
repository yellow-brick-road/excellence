---
name: tuimm-security-preflight
description: "Preflight-sast extraction procedure. Use when: extracting security findings from MR pipeline."
---

# Security Preflight — Extraction Procedure

How to extract and classify preflight-sast findings from an MR pipeline.

## Use when

- Running `$qg_security-scan`
- Running `$mr_review` security step
- Any command that needs security findings from a pipeline

## Procedure

### 1. Find the job

Via tuimm_subagent_gitlab:
- Get the pipeline for the MR's head SHA
- List jobs in that pipeline
- Find the job named `preflight-sast` in stage `test`

If no `preflight-sast` job: stop — no findings to report.
If job failed or still running: report status and stop.

### 2. Extract findings

Via tuimm_subagent_gitlab:
- Download job artifacts for the `preflight-sast` job
- Parse `preflight-junit-SAST.xml` — code-level findings
- Parse `preflight-junit-SBOM.xml` — dependency findings

JUnit format: each `<testcase>` with `<failure>` is a finding. `classname` = file path, `name` = rule/advisory, `<failure message>` = description. Severity in testcase attributes or failure message.

Fallback: if artifacts not downloadable, read job trace/log via GitLab API.

### 3. Classify SAST

For each SAST finding:
- Extract: file, line, severity, rule, description
- Check if file is in the MR diff → **🆕 NEW** (introduced by this MR)
- If file NOT in diff → **📦 PRE** (preexisting)

### 4. Classify SBOM

For each SBOM finding:
- Extract: package name, version, advisory ID, severity, description
- Deduplicate by advisory ID
- Determine prod vs dev dependency (check package.json if accessible, otherwise unknown)
- Mark as **🏭 prod** or **🔧 dev**
- Group by severity: critical → high → medium → low
