---
name: workspace-mcp
description: |
  Workspace MCP configuration pattern for TUI Nuxt projects.
  Use when: setting up a new repo for AI agents, configuring nuxt-mcp-dev,
  or troubleshooting why an agent can't see project context.
  Contains: workspace mcp.json format, nuxt-mcp-dev integration, port detection.
---

# Workspace MCP Configuration

How to configure per-project MCP servers that TUIMM agents can discover.

## How It Works

Kiro CLI loads MCP servers from two locations:
1. **Global**: `~/.kiro/settings/mcp.json` — shared across all projects
2. **Workspace**: `<project>/.kiro/settings/mcp.json` — project-specific

Agents with `includeMcpJson: true` inherit both. Other agents access workspace MCPs only if their JSON explicitly includes them.

Currently, only `tuimm-default` has `includeMcpJson: true`. Other Tier 1 agents access project-specific MCPs via subagent delegation through the default agent.

## Workspace Config for Nuxt Projects

Create `<project>/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "nuxt-dev": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:3000/__mcp/sse"]
    }
  }
}
```

This connects to the `nuxt-mcp-dev` module's MCP endpoint when the dev server is running.

### Port

Default Nuxt dev port is 3000. If the project uses a different port (via `devServer.port` in nuxt.config or `--port` flag), update the URL accordingly.

### Commit or Gitignore?

**Commit it.** The workspace MCP config is project infrastructure — all developers benefit from it. If the dev server isn't running, the MCP connection fails silently and agents continue without it.

## Prerequisites

The project must have `nuxt-mcp-dev` installed:

```bash
npm install -D nuxt-mcp-dev
```

And the module added to `nuxt.config.ts`:

```ts
export default defineNuxtConfig({
  modules: ['nuxt-mcp-dev']
})
```

## What nuxt-mcp-dev Exposes

When the dev server is running, the MCP provides:
- Resolved Nuxt configuration
- Module graph (which modules are loaded, their options)
- Project structure (pages, components, composables, layouts, middleware)
- Route definitions
- Custom tools from other modules via `mcp:setup` hook

This gives agents deep framework-aware context beyond what file reading provides.

## Graceful Degradation

If the dev server is not running:
- The MCP connection times out
- Agents continue with their other tools (shell, read, code, skills)
- No error is shown to the user — per ERROR_HANDLING steering, partial results are acceptable

## Rollout Checklist

When adding to a new or existing repo:

- [ ] `npm install -D nuxt-mcp-dev`
- [ ] Add `'nuxt-mcp-dev'` to modules in `nuxt.config.ts`
- [ ] Create `.kiro/settings/mcp.json` with the config above
- [ ] Commit all three changes
- [ ] Verify: start dev server, check `http://localhost:3000/__mcp/sse` responds
