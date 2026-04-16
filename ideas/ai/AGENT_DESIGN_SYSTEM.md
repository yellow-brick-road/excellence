# Idea: Design System Agent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

AI agent for design-to-code alignment, component governance, and design system consistency.

## Context

TUI has a design system with shared component packages and naming conventions. Keeping this consistent across teams and repos is a classic Excellence problem. This agent bridges design (Figma) and engineering (code) to ensure the design system is the single source of truth.

> Current implementation: `hc-` prefixed components, BEM methodology, `@dx/*` shared packages. The agent concepts below are framework-agnostic — the current stack is Vue/Nuxt but the patterns apply to any component-based framework.

## Subagents

- `subagent_figma` — design context, components, tokens, layout
- `subagent_gitlab` — code changes, MRs, component implementations
- `subagent_sonar` — code quality of shared components
- `subagent_weblate` — create translation keys from text extracted in Figma designs

## What It Could Do

### Design Context Extraction
- Extract component specs from Figma URLs (props, layout, spacing, colors, typography)
- Generate component scaffolds from Figma designs (framework determined by project config)
- Extract design tokens as CSS custom properties or preprocessor variables
- Compare Figma design with implemented component (visual diff)
- Pull responsive breakpoint specs from Figma frames

### Design System Governance
- Audit Figma files for design system compliance
- Detect custom/one-off components that should be in the design system
- Track design system adoption across teams (% using DS components)
- Identify inconsistencies between Figma DS and code implementation
- Flag deprecated components still in use
- Version tracking of design system components

### Design-to-Code Alignment
- Compare implemented CSS with Figma specs (detect drift)
- Generate class names from Figma component structure following project naming conventions
- Map Figma components to code components in codebase
- Detect hardcoded values that should use design tokens
- Validate naming prefix usage in both Figma and code

### Component Governance
- Shared component library mapping (Figma ↔ `@dx/*` packages)
- Compare how different teams implement the same component
- Detect divergent implementations of shared components
- Design system changelog — what changed this sprint
- Notify teams when DS components are updated
- Component deprecation workflow

### Developer Workflow
- Pull Figma context without leaving the terminal
- Auto-attach Figma links to Jira tickets
- Generate acceptance criteria from Figma annotations
- Create visual regression test baselines from Figma
- Extract icon sets and assets programmatically

### Metrics
- Design system coverage per team/project
- Design-to-code drift score
- Component reuse rate
- Time from design to implementation
- Custom vs design system components per project

## Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `ds_design_audit` | "design audit", "DS compliance" | Full design system compliance check, adoption rate |
| `ds_component_check` | "component check [name]" | Compare Figma spec vs code implementation, detect drift |
