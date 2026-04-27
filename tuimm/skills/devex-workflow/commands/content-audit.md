---
name: devex_content-audit
description: "Contentful content model health check. Use when: user says 'content audit', 'content health', or 'contentful check'."
---

# Command: $devex_content-audit

Audit Contentful content models — environment drift, unused types, freshness, TypeScript interfaces.

## Services

Ask the user which project or Contentful space to audit. If not specified, ask before proceeding.

## Process

### 1. List Content Types

Delegate to tuimm-subagent_contentful:
- List all content types in each environment (master, staging if exists)
- For each: name, ID, field count, last updated

### 2. Environment Drift

Compare content models across environments:
- Types present in one environment but not another
- Fields added/removed/changed between environments
- Flag breaking changes (removed fields, type changes)

### 3. Unused Content Types

Delegate to tuimm-subagent_contentful:
- For each content type: count entries
- Flag types with 0 entries as unused

### 4. Content Freshness

Delegate to tuimm-subagent_contentful:
- For each content type: last entry created/updated date
- Flag stale content (no updates in 6+ months)

### 5. TypeScript Interfaces

Generate TypeScript interfaces from content types:
- Map Contentful field types to TypeScript types
- Include JSDoc with field descriptions
- Output as a `.ts` file ready to use

### 6. Output

Present results using the devex-content-audit template. Follow it EXACTLY.

### 7. Ask User

- "Want me to save the TypeScript interfaces to a file?"
- "Want me to create Jira tickets for the drift issues?"

NEVER modify content models without explicit user confirmation.
