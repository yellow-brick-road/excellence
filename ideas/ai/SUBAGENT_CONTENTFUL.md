# Idea: Contentful Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Contentful CMS operations via TUI MCP Gateway.

## Context

API wrapper for Contentful. Handles content models, entries, and assets. Connected through the centralized MCP Gateway. Contentful is used across all TUI Musement frontend repos for CMS content.

No existing agent — this is new. Contentful has a Management API and Delivery API that could be exposed via MCP.

## MCP Connection

Via TUI MCP Gateway → Contentful Management API + Delivery API

## Capabilities

### Content Models
- List content types in a space/environment
- Get content type details (fields, validations, appearance)
- Compare content types across environments (dev, staging, prod)
- Get content type usage (how many entries of each type)

### Entries
- Search entries by content type, field values, tags
- Get entry details (all fields, all locales)
- Create entries
- Update entry fields
- Publish/unpublish entries
- Archive entries
- Bulk operations (publish, unpublish, delete)

### Assets
- List assets
- Get asset details (URL, dimensions, file type)
- Upload assets
- Search assets by filename, type

### Environments
- List environments
- Compare environments (content model diff)
- Get environment status

### Locales
- List configured locales
- Get entry content per locale
- Detect missing translations per locale

### Intelligence (light)
- Generate TypeScript interfaces from content types
- Detect empty or incomplete entries
- Find orphan entries (not referenced anywhere)
- Detect content model drift between environments
- Calculate content freshness (last updated)

## Used By

- DevEx Agent → content model management, TypeScript generation, content audits
- Knowledge Agent → sync CMS documentation
- Excellence Default → ad-hoc content queries
