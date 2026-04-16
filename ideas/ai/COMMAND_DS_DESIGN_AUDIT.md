# Command: $design-audit

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `ds_design_audit`
> Description: Full design system compliance check. Compare Figma designs with code, detect drift, measure DS adoption rate per project.
> Agent: Design System

## Trigger

`$design-audit` or "design audit", "design system check", "DS compliance"

## Workflow

1. `subagent_figma` → extract design system components and tokens
2. `subagent_gitlab` → scan codebase for `hc-` prefixed components
3. Compare: Figma DS components vs code implementations
4. Detect drift (CSS values that don't match design tokens)
5. Detect custom components that should use DS components
6. `subagent_sonar` → check quality of shared DS components
7. Calculate DS adoption rate per team/project

## Output

- DS component inventory (Figma vs code)
- Design-to-code drift (mismatched values)
- Custom components that should be DS components
- DS adoption rate per project
- Deprecated components still in use
- Quality of shared components (SonarQube)

## Phase

Phase 2 (requires Figma subagent)
