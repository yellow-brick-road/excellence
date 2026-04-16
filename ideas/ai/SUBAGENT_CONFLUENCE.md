# Idea: Confluence Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Confluence documentation operations via TUI MCP Gateway.

## Context

API wrapper for Confluence. Handles page creation, search, and space management. Connected through the centralized MCP Gateway. The Atlassian MCP already supports Confluence alongside Jira, so the infrastructure exists.

No existing agent — this is new.

## MCP Connection

Via TUI MCP Gateway → Confluence Cloud API (Atlassian)

## Capabilities

### Read
- Search pages across spaces (CQL queries)
- Get page content (body, metadata, labels, version)
- List pages in a space
- Get page hierarchy (parent/child relationships)
- Get page comments
- Get page history (versions, who changed what)
- List spaces and their configuration

### Write
- Create pages (with Atlassian Storage Format)
- Update page content
- Add/remove labels
- Add comments to pages
- Move pages between spaces/parents
- Create pages from templates
- Archive/delete pages

### Templates
- RFC template
- ADR (Architecture Decision Record) template
- Runbook template
- How-to guide template
- Sprint retrospective template
- Incident report template
- Onboarding guide template

### Intelligence (light)
- Detect stale pages (not updated in X months)
- Find orphan pages (no incoming links)
- Detect duplicate content across pages
- Check for broken links
- Calculate page freshness score

## Used By

- Knowledge Agent → documentation health, creation, search, governance
- Observability Agent → incident reports, runbooks
- DevEx Agent → sprint retrospectives, release notes
- Excellence Default → ad-hoc documentation queries
