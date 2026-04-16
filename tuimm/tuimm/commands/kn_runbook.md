---
name: kn_runbook
description: "Generate runbook from existing knowledge. Use when: user says 'runbook [topic]', 'create runbook', or 'generate runbook'."
---

# Command: $kn_runbook

Generate a runbook for a specific topic — synthesize incidents, code, and docs into a Confluence page.

## Inputs

- **topic**: required. What the runbook is about (e.g., "deployment rollback", "Datadog alerting", "Contentful migration").

## Process

### 1. Search Existing Knowledge

Delegate to tuimm_subagent_confluence:
- Search for pages related to the topic
- Collect relevant content, procedures, notes

### 2. Get Incident History

Delegate to tuimm_observability (cross-agent):
- Request historical incidents related to the topic
- What went wrong, how it was resolved, timeline

If tuimm_observability is not available, skip this step and note it in the output.

### 3. Get Code Context

Delegate to tuimm_subagent_gitlab:
- Find relevant code, configs, scripts related to the topic
- CI/CD pipeline definitions if deployment-related
- Environment configs if infrastructure-related

### 4. Synthesize Runbook

Combine all sources into a structured runbook:

```markdown
# Runbook: {topic}

## Overview
What this runbook covers and when to use it.

## Prerequisites
- Access needed (tools, environments, permissions)
- Tools required

## Procedure
Step-by-step instructions with commands and expected outputs.

## Troubleshooting
Common issues and how to resolve them (from incident history).

## Escalation
Who to contact if the procedure doesn't resolve the issue.

## Related
Links to related documentation, code, and incidents.

## History
- Created: {date}
- Based on: {sources used}
```

### 5. Present Draft

Show the runbook draft to the user for review.

**Wait for user confirmation before creating the Confluence page.**

### 6. Create Page

On approval, delegate to tuimm_subagent_confluence:
- Create page in the appropriate space
- Apply runbook template/labels
- Link to related pages

### 7. Output

Present results using the kn-runbook template. Follow it EXACTLY — LAST STEP, nothing after this.
