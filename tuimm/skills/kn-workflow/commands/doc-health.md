---
name: kn_doc-health
description: "Documentation health audit across Confluence. Use when: user says 'doc health', 'docs audit', or 'documentation health'."
---

# Command: $kn_doc-health

Documentation health audit — stale pages, orphans, broken links, freshness scores, coverage.

## Inputs

- **space**: Confluence space key(s). If not provided, ask before proceeding.

## Process

### 1. Inventory

Delegate to tuimm-subagent_confluence:
- List all pages in the space(s)
- For each: title, last updated date, author, parent page, labels

### 2. Stale Pages

Flag pages not updated in 6+ months:
- Page title, last update date, author
- Check if referenced code has changed since last update (via gitlab subagent)

### 3. Orphan Pages

Delegate to tuimm-subagent_confluence:
- Find pages with no incoming links from other pages
- Exclude root/index pages

### 4. Broken Links

Delegate to tuimm-subagent_confluence:
- Scan page content for links
- Check if linked pages still exist
- Check if external URLs are reachable

### 5. Freshness Score

Per space/team:
- Average age of last update across all pages
- % of pages updated in last 3 months
- % of pages older than 12 months

### 6. Minimum Docs Check

For each project (cross-reference with gitlab subagent):
- README exists?
- Architecture/design doc exists?
- Deployment/runbook doc exists?
- Onboarding doc exists?

### 7. Output

Present results using the kn-doc-health template. Follow it EXACTLY — LAST STEP, nothing after this.
