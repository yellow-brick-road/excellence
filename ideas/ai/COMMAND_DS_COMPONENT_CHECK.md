# Command: $component-check

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `ds_component_check`
> Description: Compare a specific component's Figma design spec with its code implementation. Detect visual drift, missing props, naming issues.
> Agent: Design System

## Trigger

`$component-check [name]` or "check component", "compare component"

## Workflow

1. `subagent_figma` → extract component spec (props, variants, spacing, colors, typography)
2. `subagent_gitlab` → find component implementation in codebase
3. Compare: Figma props vs component props
4. Compare: Figma spacing/colors vs CSS values
5. Check naming conventions (project-configured prefix and methodology)
6. Check accessibility (ARIA attributes, keyboard navigation)
7. `subagent_sonar` → check component code quality

## Output

- Component: Figma spec vs code implementation
- Props comparison (missing, extra, type mismatches)
- Visual drift (spacing, colors, typography differences)
- Naming convention compliance
- Accessibility issues
- Code quality (SonarQube)
- Recommended fixes

## Phase

Phase 2 (requires Figma subagent)
