# Templates

Output format definitions. Commands reference them to ensure consistent, structured output across agents.

## How they work

A command says "present results using the mr-review-summary template." The agent reads the template, which defines the exact structure: sections, fields, formatting rules. This way every MR review looks the same regardless of which session produced it.

## Naming

Templates match their command: `mr_review` → `mr-review-summary.md`, `obs_dd-scan` → `obs-scan-summary.md`, `dev_solve` → `dev-solve.md`.

Special templates:
- `template-blueprint.md` — reference for creating new templates
- `guidelines-generator/extract.md` — prompt template for the guidelines-generator tool

## How they load

Agents load templates as skills alongside commands:

```json
{
  "resources": [
    { "type": "skill", "path": "~/.kiro/tuimm/templates/*.md" }
  ]
}
```

The agent reads the template when a command references it — not at startup.
