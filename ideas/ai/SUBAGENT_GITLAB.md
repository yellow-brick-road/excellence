# Idea: GitLab Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for GitLab operations via TUI MCP Gateway.

## Context

API wrapper for GitLab. Handles MRs, branches, pipelines, and repository operations. Connected through the centralized MCP Gateway. Used by almost every Tier 1 agent — GitLab is the backbone of the development workflow.

Based on existing `subagent_gitlab` which uses GitLab MCP API.

## MCP Connection

Via TUI MCP Gateway → GitLab API (`source.tui`)

## Capabilities

### Merge Requests
- List MRs (by project, author, status, labels)
- Get MR details (description, diff, discussions, approvals)
- Create MRs (with description, labels, assignees, reviewers)
- Update MRs (title, description, labels, reviewers)
- Add comments and inline comments to MRs
- Resolve/unresolve discussion threads
- Approve/unapprove MRs
- Merge MRs (with merge options)

### Branches
- List branches (with activity info)
- Create branches from source
- Delete branches
- Compare branches (diff)
- Generate feature branch URLs (`tuimusement-{branch}.dev.musement.com`)

### Pipelines
- Get pipeline status (running, passed, failed)
- Get pipeline jobs and their status
- Retry failed jobs
- Cancel running pipelines
- Get pipeline artifacts

### Repository
- Get file content from repo
- List directory contents
- Get commit history
- Compare commits/tags
- Get CODEOWNERS

### Intelligence (light)
- Auto-populate MR description from commits and linked Jira ticket
- Detect MR size (warn if too large)
- Auto-label MRs based on changed files
- Detect stale branches (no activity in X days)
- Cross-repo dependency impact ("changing @dx/b2c-foundation affects these repos")

## Used By

- Quality Guardian → MR quality checks, code change analysis
- Observability Agent → correlate errors with deploys, recent MRs
- DevEx Agent → MR workflow, branch hygiene, pipeline monitoring
- Design System Agent → component implementation changes
- Knowledge Agent → sync docs, extract MR data for release notes
- Excellence Default → ad-hoc git operations
