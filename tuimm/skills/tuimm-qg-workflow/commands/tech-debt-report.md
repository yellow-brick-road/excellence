---
name: qg_tech-debt-report
description: "Technical debt quantification and prioritization. Use when: user says 'tech debt', 'debt report', or 'technical debt'."
---

# Command: $qg_tech-debt-report

Quantify and prioritize technical debt. Hotspots, trends, ROI analysis, cleanup plan.

## Services

Ask the user which projects to analyze. If not specified, ask before proceeding.

## Process

### 1. Debt Metrics

Delegate to tuimm_subagent_sonar for each project:
- Total debt (hours/days)
- Debt by category: reliability, security, maintainability
- Reliability, security, maintainability ratings (A-E)

### 2. Hotspots

Delegate to tuimm_subagent_sonar:
- Top 10 files with most debt per project
- For each: file path, debt (hours), issue count, complexity

### 3. Trends

Delegate to tuimm_subagent_sonar:
- Debt trend over last 4 analyses
- Growing or shrinking per category

### 4. ROI Analysis

Calculate for top hotspots:
- Effort to fix (hours from SonarQube)
- Debt reduction percentage if fixed
- Rank by ROI: highest debt reduction per hour of effort

### 5. Existing Tickets

Delegate to tuimm_subagent_jira:
- Search for existing tech debt tickets related to the hotspot files
- Flag hotspots with no ticket (untracked debt)

### 6. Production Impact

Delegate to tuimm_subagent_datadog:
- Check if any debt hotspot files correlate with production errors
- Prioritize debt that causes real user impact

### 7. Output

Present results using the qg-tech-debt-report template. Follow it EXACTLY — LAST STEP, nothing after this.
