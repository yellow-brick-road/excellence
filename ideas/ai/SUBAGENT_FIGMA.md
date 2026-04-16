# Idea: Figma Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Figma design context extraction via TUI MCP Gateway.

## Context

API wrapper for Figma. Extracts design context, components, tokens, and layout information. Connected through the centralized MCP Gateway. Primarily used by the Design System agent.

Based on existing `subagent_figma` which uses Framelink MCP (`mcp.figma.com`).

## MCP Connection

Via TUI MCP Gateway → Figma API

## Capabilities

### Design Context
- Extract design context from Figma URLs (frames, components, groups)
- Get layout and styling information (spacing, colors, typography, borders)
- Get simplified design data optimized for code generation
- Extract responsive breakpoint specs from frames

### Components
- List components in a file/page
- Get component properties (props, variants, states)
- Get component instances and where they're used
- Extract component structure (layers, hierarchy)

### Design Tokens
- Extract color tokens
- Extract spacing/sizing tokens
- Extract typography scales
- Extract shadow, border, and effect tokens
- Export tokens as CSS custom properties or preprocessor variables

### Assets
- Extract icon sets
- Export assets (SVG, PNG)
- Get image fills and their URLs

### Intelligence (light)
- Map Figma components to code components (using project-configured prefix)
- Detect design system compliance (using DS components vs custom)
- Compare design specs with code class structure
- Generate component scaffold from design (framework determined by project config)

## Used By

- Design System Agent → design-to-code alignment, component governance, token extraction
- Excellence Default → ad-hoc design queries
