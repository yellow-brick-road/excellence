# Idea: TUI MCP Gateway

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Centralized MCP gateway for secure, audited, role-based access to all TUI tools.

## Context

Instead of every developer having API keys for 9+ tools on their laptop, TUI builds a single MCP endpoint that handles authentication, authorization, and auditing centrally. Developers connect their agents to one gateway — no credentials on local machines, no key rotation headaches, no security risk from leaked tokens.

This is the infrastructure layer that makes the entire Excellence AI architecture secure and scalable.

## The Problem

```
CURRENT: Credentials everywhere

Dev A laptop: jira_key, gitlab_token, sonar_key, datadog_key, figma_key...
Dev B laptop: jira_key, gitlab_token, sonar_key, datadog_key, figma_key...
Dev C laptop: jira_key, gitlab_token, sonar_key, datadog_key, figma_key...

→ 9 tools × N developers = N×9 credential sets floating around
→ Key rotation = update every developer's config
→ Offboarding = hope they deleted their keys
→ Audit = impossible
```

## The Solution

```
PROPOSED: Centralized MCP Gateway

Dev A laptop ──→ ┌─────────────────────────────────┐
Dev B laptop ──→ │  TUI MCP Gateway                │
Dev C laptop ──→ │  https://mcp.tui.internal/v1/sse│
                 │                                   │
                 │  ┌─────┐ ┌──────┐ ┌─────┐       │
                 │  │Jira │ │GitLab│ │Sonar│  ...   │
                 │  └─────┘ └──────┘ └─────┘       │
                 │                                   │
                 │  • SSO/OAuth authentication       │
                 │  • Role-based access (RBAC)       │
                 │  • Audit logging                  │
                 │  • Rate limiting                  │
                 │  • Credentials in vault           │
                 │  • Tool-level permissions          │
                 └─────────────────────────────────┘

→ 0 credentials on laptops
→ Key rotation = update vault, zero developer impact
→ Offboarding = disable SSO account, instant revocation
→ Audit = complete log of every tool call by every user
```

## Architecture

### Authentication
- SSO/OAuth2 via TUI's identity provider
- Developer authenticates once, gateway handles tool-specific auth
- Token refresh handled transparently
- Session management with configurable timeouts

### Authorization (RBAC)
- Role-based permissions per tool and action
- Examples:
  - Junior dev: read Jira, read GitLab, read SonarQube. No write.
  - Senior dev: read/write Jira, read/write GitLab, read SonarQube, read Datadog.
  - Tech lead: full access to all tools.
  - Excellence team: full access + admin operations.
- Team-scoped access (can only see your team's projects/repos)
- Action-level granularity (can create MRs but not merge, can read flags but not toggle prod)

### Audit Logging
- Every tool call logged: who, what tool, what action, when, from where
- Searchable audit trail
- Anomaly detection (unusual access patterns)
- Compliance reporting
- Retention policy (configurable)

### Rate Limiting
- Per-user rate limits to prevent API abuse
- Per-tool rate limits to respect upstream API quotas
- Burst allowance for legitimate batch operations
- Configurable per role

### Credential Management
- All API keys/tokens stored in vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- Automatic rotation on schedule
- Zero developer exposure to raw credentials
- Per-environment credentials (dev, staging, prod)

### Kill Switch
- Instant revocation per user, per team, or per tool
- Emergency disable for compromised credentials
- Graceful degradation (disable one tool without affecting others)

## MCP Protocol

### Connection
- HTTP Remote MCP endpoint: `https://mcp.tui.internal/v1/sse`
- Agents connect via `mcp-remote` (same as Atlassian and Figma MCPs today)
- SSE (Server-Sent Events) for streaming responses

### Agent Configuration
```json
{
  "mcpServers": {
    "tui-gateway": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.tui.internal/v1/sse"],
      "env": { "TUI_SSO_TOKEN": "${TUI_SSO_TOKEN}" }
    }
  }
}
```

One MCP server config instead of nine. All tools accessible through the same connection.

### Tool Namespacing
Tools are namespaced by service:
- `jira.search_issues`, `jira.create_issue`, `jira.add_comment`
- `gitlab.list_mrs`, `gitlab.create_mr`, `gitlab.get_pipeline`
- `sonar.get_quality_gate`, `sonar.search_issues`
- `datadog.search_logs`, `datadog.get_metrics`
- `figma.get_design_context`
- `confluence.search_pages`, `confluence.create_page`
- `contentful.list_entries`, `contentful.get_content_type`
- `configcat.list_flags`, `configcat.toggle_flag`
- `weblate.add_key`, `weblate.get_coverage`
- `search.web`, `search.web_premium`, `search.extract`, `search.deep`

## Implementation Options

### Option 1: HTTP Remote MCP (Recommended)
- Nitro (Node.js) service implementing MCP protocol
- Proxies to upstream tool APIs
- Deployed as internal service (Kubernetes, ECS, etc.)
- Easiest to build, most aligned with MCP ecosystem

### Option 2: API Gateway + MCP Adapters
- AWS API Gateway or Kong as the entry point
- MCP protocol adapter per tool behind the gateway
- Enterprise-grade but more complex
- Better for very large orgs with existing API gateway infra

### Option 3: Aggregator MCP Server
- Single MCP server binary that bundles all tool adapters
- Distributed to developers as a CLI tool
- Credentials fetched from vault at runtime
- Simpler deployment but credentials still flow through developer machines

## Implementation Phases

### Phase 1: Core Gateway
- SSO authentication
- Jira, GitLab, SonarQube, Datadog adapters (most used tools)
- Deploy SearXNG, add search.* namespace
- Basic audit logging
- Rate limiting

### Phase 2: Full Tool Coverage
- Add Figma, Confluence, Contentful, ConfigCat, Weblate
- Add Tavily and Brave to search (premium engines)
- RBAC with role definitions
- Advanced audit logging and anomaly detection

### Phase 3: Enterprise Features
- Team-scoped access
- Action-level permissions
- Compliance reporting
- Kill switch and emergency controls
- Self-service onboarding for new teams

## Benefits for Excellence

- **Security**: Zero credentials on developer machines
- **Governance**: Full audit trail of all tool interactions
- **Scalability**: Onboard new teams by assigning roles, not distributing keys
- **Consistency**: All teams use the same tool interfaces
- **Control**: RBAC ensures appropriate access levels
- **Maintainability**: Credential rotation is centralized, zero developer impact
- **Compliance**: Audit logs for security reviews and compliance requirements
