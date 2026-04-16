# TUIMM Agents — Setup

## 1. Install the package

```bash
# Create dirs if they don't exist
mkdir -p ~/.kiro/agents ~/.kiro/tuimm

# Copy agent configs
cp agents/*.json ~/.kiro/agents/

# Copy the package
cp -r tuimm/* ~/.kiro/tuimm/
```

Verify the structure:

```bash
ls ~/.kiro/agents/tuimm_*.json    # should list 19 files
ls ~/.kiro/tuimm/steering/        # should list 11 .md files
ls ~/.kiro/tuimm/commands/        # should list 35 .md files
```

## 2. Configure credentials

Environment variables required by TUIMM subagents. Add these to your shell config and restart your terminal.

| OS | Shell config file |
|----|-------------------|
| Linux / WSL | `~/.bashrc` |
| macOS | `~/.zshrc` (default since Catalina) |

**Important**: Agent JSON `env` blocks do NOT support `${VAR}` interpolation. Instead, MCP servers inherit environment variables from the parent kiro-cli process. Export the standard variable names that each MCP server expects.

**⚠️ Critical**: You must have the env vars exported BEFORE starting `kiro-cli`. If you add a new export to `~/.bashrc` and `source` it, that only affects the current shell — any already-running `kiro-cli` session won't see the new var. Either:
- Open a new terminal and launch `kiro-cli` from there, or
- Stop and restart `kiro-cli` in the same terminal after sourcing

### Required Variables

### GitLab

```bash
export GITLAB_PERSONAL_ACCESS_TOKEN="<your-gitlab-personal-access-token>"
```

Get your token at: https://source.tui/-/user_settings/personal_access_tokens
Scopes needed: `api`, `read_repository`, `write_repository`

### Datadog

```bash
export DD_API_KEY="<your-datadog-api-key>"
export DD_APP_KEY="<your-datadog-app-key>"
```

Get your keys at: https://tui-musement.datadoghq.eu/organization-settings/api-keys

### SonarQube

```bash
export SONARQUBE_TOKEN="<your-sonarqube-token>"
```

Get your token at: https://sonarqube.devops.tui/account/security

Requires VPN connection. Uses community MCP package (`sonarqube-mcp-server@1.10.21`) — see Known Issues below.

### Jira

No env var needed — uses OAuth via browser (mcp-remote). On first use, a browser window opens for authentication. Tokens are cached in `~/.mcp-auth/`.

### Confluence

Same Atlassian OAuth as Jira — no additional setup needed. Shares the same `mcp-remote` connection.

### Figma

```bash
export FIGMA_API_KEY="<your-figma-personal-access-token>"
```

Get your token at: https://www.figma.com/settings → **Personal access tokens** → Generate new token.

Scopes needed (all read):
- `current_user:read`
- `file_content:read`
- `file_metadata:read`
- `file_comments:read`
- `file_versions:read`
- `file_dev_resources:read`
- `library_assets:read`
- `library_content:read`
- `team_library_content:read`
- `projects:read`
- `webhooks:read`

No write scopes needed — agents only read design context.

### Contentful

```bash
export CONTENTFUL_MANAGEMENT_ACCESS_TOKEN="<your-cma-token>"
```

Get your token at: https://app.contentful.com/account/profile/cma_tokens
Space ID (`m0d454rkzj24`) and environment (`master`) are pre-configured in the agent.

### ConfigCat

```bash
export CONFIGCAT_API_USER="<your-api-user>"
export CONFIGCAT_API_PASS="<your-api-password>"
```

Get your credentials at: https://app.configcat.com/my-account/public-api-credentials
Save the password — it's only shown once.

### Nuxt (no setup needed)

The Nuxt documentation subagent connects to `nuxt.com/mcp` via `mcp-remote`. Public endpoint — no credentials, no env vars. Works out of the box via `npx`.

## 3. Quick Setup

```bash
# Detect shell config
SHELL_RC="$HOME/.bashrc"
[ "$(basename "$SHELL")" = "zsh" ] && SHELL_RC="$HOME/.zshrc"

# Add exports
cat >> "$SHELL_RC" << 'EOF'

# TUIMM agent credentials
export GITLAB_PERSONAL_ACCESS_TOKEN="<your-token>"
export DD_API_KEY="<your-dd-api-key>"
export DD_APP_KEY="<your-dd-app-key>"
export SONARQUBE_TOKEN="<your-sonar-token>"
export FIGMA_API_KEY="<your-figma-token>"
export CONTENTFUL_MANAGEMENT_ACCESS_TOKEN="<your-cma-token>"
export CONFIGCAT_API_USER="<your-api-user>"
export CONFIGCAT_API_PASS="<your-api-password>"
EOF

# Reload
source "$SHELL_RC"
```

## 4. Verify

```bash
echo $GITLAB_PERSONAL_ACCESS_TOKEN  # should print your token
echo $DD_API_KEY                    # should print your Datadog API key
```

Then launch any TUIMM agent to verify everything works:

```bash
kiro-cli --agent tuimm_default
```

Type `$get-commands` — if it lists all 35 commands across 9 agents, you're good.

**Note**: On first launch, `npx` downloads MCP packages which can timeout in kiro-cli. If a server shows "still loading", just try again — the package will be cached from the first attempt.

## How It Works

MCP servers run as child processes of kiro-cli. Child processes inherit the parent's environment variables. The agent JSON `env` block only sets non-secret config (API URLs, flags). Secrets come from the shell environment.

## Optional: nuxt-mcp-dev

`nuxt-mcp-dev` is a Nuxt module by antfu that exposes your app's internal runtime state (module graph, resolved config, routes, components) to AI tools via MCP. It gives agents deep project context beyond just reading files.

### Setup

1. Install as dev dependency:
```bash
npm install -D nuxt-mcp-dev
```

2. Add to `nuxt.config.ts`:
```ts
export default defineNuxtConfig({
  modules: ['nuxt-mcp-dev']
})
```

3. Add workspace MCP config (see `workspace-mcp` skill for the pattern):
```
<project>/.kiro/settings/mcp.json
```

When the dev server runs, the MCP endpoint is available at `http://localhost:3000/__mcp/sse`. Agents with `includeMcpJson: true` (tuimm_default) pick it up automatically. Other agents that need it must add the MCP server explicitly to their `mcpServers` config.

If the dev server is not running, the MCP connection fails silently — agents continue without it.

### Rollout

This should be added to:
- **Repo templates** — include `nuxt-mcp-dev` in devDependencies and the workspace MCP config in `.kiro/settings/mcp.json`
- **`tui fe init`** (future CLI) — scaffold the module + workspace config automatically
- **Onboarding DX** — mention in README template as part of AI-enhanced development

## Known Issues

### SonarQube MCP: community package instead of official

The official SonarQube MCP Server by SonarSource (`mcp/sonarqube`, Docker-based) does NOT expose a `branch` parameter on its tools (`get_project_quality_gate_status`, `get_component_measures`, `search_sonar_issues_in_projects`). It only queries the project's default branch.

At TUI, many projects have `main` set as default branch in SonarQube but run analysis on `master`. Without the `branch` parameter, the official MCP returns empty data.

The underlying SonarQube API supports `&branch=master` — the MCP just doesn't expose it.

**Workaround**: We use the community npm package `sonarqube-mcp-server@1.10.21` (by sapientpants) which supports branch parameters. It's deprecated on npm but functional and pinned to a specific version.

**When to revisit**: If SonarSource adds branch support to the official MCP, or if TUI migrates to SonarQube Cloud.

Investigated: 2026-04-07. Official MCP tool schemas dumped via JSON-RPC — confirmed no branch parameter on any tool.
