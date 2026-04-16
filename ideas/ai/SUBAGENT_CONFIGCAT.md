# Idea: ConfigCat Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for ConfigCat feature flag operations via TUI MCP Gateway.

## Context

API wrapper for ConfigCat. Handles feature flags, targeting rules, and A/B test configuration. Connected through the centralized MCP Gateway. ConfigCat is used across all TUI Musement repos for feature flags and experimentation.

No existing agent — this is new. ConfigCat has a Public Management API that can be exposed via MCP.

## MCP Connection

Via TUI MCP Gateway → ConfigCat Public Management API

## Capabilities

### Flags
- List feature flags (by config, environment, tag)
- Get flag details (value, targeting rules, percentage rollout)
- Create flags with naming conventions
- Update flag values per environment
- Toggle flags on/off per environment
- Delete flags
- Get flag history (changes over time)

### Targeting
- Get targeting rules for a flag
- Update targeting rules
- Get segment definitions
- Compare targeting across environments

### Environments
- List environments
- Compare flag states across environments (dev, staging, prod)
- Promote flag configuration between environments

### A/B Testing
- Get experiment configurations
- Get experiment results (if available via API)
- List active experiments

### Audit
- Get audit log (who changed what, when)
- Track flag changes over time

### Intelligence (light)
- Detect stale flags (enabled for X months, never toggled)
- Find flags at 100% rollout (cleanup candidates)
- Detect conflicting targeting rules
- Flag naming convention validation
- Calculate flag age distribution

## Used By

- DevEx Agent → flag lifecycle, cleanup, A/B testing, hygiene
- Observability Agent → correlate errors with flag changes
- Excellence Default → ad-hoc flag queries
