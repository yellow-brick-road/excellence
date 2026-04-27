---
name: obs_dd-investigate
description: |
  Deep root cause analysis for a production error. Use when: user says 'investigate [error]',
  'root cause [error]', or wants to understand why a specific error is happening.
---

# Command: $obs_dd-investigate

Deep root cause analysis with cross-service correlation.

## Inputs

- **error**: Error message, pattern, or Datadog log ID
- **service**: Service name (if known). If not provided, detect from error context
- **time_range**: Time range to search (default: last 24h)

## Process

### 1. Gather Error Context

Via tuimm-subagent_datadog:
- Search for the error pattern in logs
- Get full stack trace from a representative log entry
- Check error frequency and timeline (when did it start? spike or steady?)
- Check affected endpoints/pages

### 2. Trace Origin

Read source code to understand the error:
- Use tuimm-subagent_gitlab to fetch the file and line from the stack trace
- Or grep/glob on local code if the repo is cloned
- Trace the call chain backward — where does the data come from?

### 3. Correlate with Changes

Via tuimm-subagent_gitlab:
- Check recent deploys and MRs merged around the time the error started
- Compare error timeline with deploy timestamps
- Identify which MR might have introduced the issue

### 4. Cross-Service Correlation

If the error involves API calls or external services:
- Check upstream service logs via tuimm-subagent_datadog
- Trace request flow: frontend → API → database
- Check if the upstream service has its own errors in the same time window

### 5. Check Related Systems

- Feature flags: via tuimm-subagent_configcat — any recent flag changes that could affect this code path?
- Code quality: via tuimm-subagent_sonar — any known issues in the affected files?

### 6. Root Cause Analysis

Synthesize findings into a hypothesis:
- What changed? (deploy, flag, data, external service)
- Why does it fail? (null value, timeout, wrong format, missing config)
- What's the impact? (frequency, affected users, business impact)

**Do NOT propose "add null check" without understanding WHY it's null.**

### 7. Output

Present results using the obs-investigate template. Follow it EXACTLY — LAST STEP, nothing after this.
