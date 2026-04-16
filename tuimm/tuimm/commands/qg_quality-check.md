---
name: qg_quality-check
description: "Full quality scan across projects. Use when: user says 'quality check', 'quality scan', or 'check quality'."
---

# Command: $qg_quality-check

Full quality scan — quality gates, new issues, coverage, cross-project comparison.

## Services

Ask the user which projects to scan. If not specified, ask before proceeding.

## Process

### 1. Quality Gate Status

Delegate to tuimm_subagent_sonar for each project:
- Quality gate status (PASSED/FAILED)
- Conditions that failed (if any)

### 2. New Issues

Delegate to tuimm_subagent_sonar for each project:
- New issues since last analysis, grouped by severity (blocker, critical, major, minor)
- For blockers and criticals: file, line, rule, message

### 3. Coverage

Delegate to tuimm_subagent_sonar for each project:
- Current coverage percentage
- Coverage on new code
- Trend vs previous analysis

### 4. Tech Debt Summary

Delegate to tuimm_subagent_sonar for each project:
- Total debt (hours/days)
- Reliability, security, maintainability ratings

### 5. Cross-Project Comparison

Compare all scanned projects:
- Detect outliers (significantly worse quality gate, coverage, or debt)
- Highlight projects with declining trends

### 6. MR Impact

Delegate to tuimm_subagent_gitlab:
- Check if any open MRs are blocked by failing quality gates

### 7. Production Correlation (optional)

If user requests or if critical issues found:
- Delegate to tuimm_subagent_datadog to check if quality issues correlate with production errors

### 8. Output

Present results using the qg-quality-check template. Follow it EXACTLY — LAST STEP, nothing after this.
