# Practice: Auto Documentation

## Guild Position

> Best practices should be extracted from real code, not written from memory. Auto-generate global and per-team documentation that agents consume as skills/steering. Living docs that stay in sync with how the code actually works.

## What

Automated generation of best practices documentation by analyzing actual repo code patterns. Two scopes:

- **Global** — cross-team conventions: naming, git, TypeScript, CSS/BEM, testing, accessibility
- **Per-team/repo** — specific patterns: composables, store patterns, API conventions, component structure

## Output Format

Each generated doc follows the skill format:

- **name** — short identifier (e.g. `vue-composable-patterns`, `b2c-api-conventions`)
- **description** — what it covers and when to load it (used by agents to decide relevance)
- **content** — extracted patterns with real code examples from the repo

## How

1. Analyze repos — scan for recurring patterns, conventions, anti-patterns
2. Extract examples — real code snippets, not theoretical
3. Generate markdown — skill-compatible format (name + description + content)
4. Detect drift — periodic re-scan to find divergence between docs and actual code
5. Update — regenerate when patterns evolve

## Scope

| Level | Examples | Source |
|-------|----------|--------|
| Global | Naming conventions, git workflow, TS strict patterns, BEM | All repos |
| Team/Repo | Composable patterns, store structure, API layer, test helpers | Specific repo |

## Consumers

- AI agents (as skills or steering files)
- Developers (onboarding, reference)
- Code reviewers ("is this how we do it?")

## Status

> Status: Idea — already being done manually with Kiro in another repo. Goal: standardize and automate.
