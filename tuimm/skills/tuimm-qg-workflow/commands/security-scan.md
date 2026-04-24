---
name: qg_security-scan
description: "Security scan of MR pipeline findings. Use when: user says 'security scan [MR]', 'preflight [MR]', or 'security findings'."
---

# Command: $qg_security-scan

Analyze preflight-sast findings from an MR pipeline — classify SAST vs SBOM, distinguish new vs preexisting, recommend action.

## Process

### 1. Get MR Context

Parse MR URL or ask for project + IID. Delegate to tuimm_subagent_gitlab:
- Fetch MR info (source branch, target branch, changed files list)
- Fetch MR diff (list of changed file paths)

### 2. Find Preflight Job

Follow the tuimm-security-preflight skill for steps 1-4 (find job → extract findings → classify SAST → classify SBOM).

The skill needs the MR diff (from Step 1) to classify SAST findings as NEW vs PREEXISTING.

If no `preflight-sast` job exists: inform the user and stop. Do not proceed.

If the job failed or is still running: inform the user of the status and stop.

### 3. Output

Present results using the qg-security-scan template. Follow it EXACTLY — LAST STEP, nothing after this.
