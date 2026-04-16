# Idea: SonarQube Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for SonarQube code quality operations via TUI MCP Gateway.

## Context

API wrapper for SonarQube. Queries issues, quality gates, metrics, and coverage data. Connected through the centralized MCP Gateway. Primarily used by Quality Guardian and Observability agents.

Based on existing `subagent_sonar` which uses SonarQube MCP API.

## MCP Connection

Via TUI MCP Gateway → SonarQube API

## Capabilities

### Quality Gates
- Get quality gate status per project
- Get quality gate conditions and thresholds
- Compare quality gate configs across projects
- Get quality gate history (pass/fail over time)

### Issues
- Search issues by project, severity, status, type, rule
- Get issue details (location, message, effort, assignee)
- Get issue changelog (when created, when resolved)
- Bulk search across multiple projects
- Filter by new issues (since last analysis) vs existing

### Metrics
- Get project metrics (bugs, vulnerabilities, code smells, coverage, duplications)
- Get metric history (trends over time)
- Compare metrics across projects
- Get complexity metrics (cognitive, cyclomatic)
- Get maintainability and reliability ratings

### Coverage
- Get overall coverage percentage
- Get coverage per file/directory
- Get uncovered lines/conditions
- Get coverage on new code vs overall

### Rules
- Get rule details (description, severity, type)
- List active rules per quality profile
- Compare quality profiles across projects

### Intelligence (light)
- Categorize issues by impact (security > bugs > code smells)
- Group related issues (same root cause pattern)
- Identify hotspot files (most issues concentrated)
- Calculate tech debt in hours/days

## Used By

- Quality Guardian → quality monitoring, debt management, coverage tracking
- Observability Agent → correlate code quality with production errors
- Design System Agent → shared component quality
- Excellence Default → ad-hoc quality queries
