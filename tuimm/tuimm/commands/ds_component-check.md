---
name: ds_component-check
description: "Compare Figma spec vs code implementation for a component. Use when: user says 'component check [name]' or 'compare component'."
---

# Command: $ds_component-check

Compare a specific component's Figma design spec with its code implementation.

## Inputs

- **component name**: required. Figma component name or code component name.
- **Figma URL**: optional. If provided, extract directly. If not, search Figma for the component name.

## Process

### 1. Extract Figma Spec

Delegate to tuimm_subagent_figma:
- Component props and variants
- Spacing (padding, margin, gap)
- Colors (background, text, border)
- Typography (font, size, weight, line-height)
- Responsive behavior (breakpoints, layout changes)

### 2. Find Code Implementation

Search codebase for the component:
- Check shared packages and local components
- Read the full component file (template, script, styles)
- Extract: props interface, emits, slots, CSS

### 3. Compare Props

| Figma Prop | Code Prop | Status |
|------------|-----------|--------|
| {name} | {name} | ✅ Match / ❌ Missing / ⚠️ Type mismatch |

### 4. Compare Visual Specs

| Property | Figma | Code | Status |
|----------|-------|------|--------|
| padding | 16px | 1rem | ✅ Equivalent |
| color | #1A1A1A | var(--text-primary) | ✅ Token |
| font-size | 14px | 14px (hardcoded) | ⚠️ Should use token |

### 5. Naming Conventions

- Check component name follows project prefix convention
- Check CSS class names follow project methodology
- Check file location matches project structure

### 6. Accessibility

- ARIA attributes present where needed
- Keyboard navigation support
- Color contrast (compare Figma colors)
- Focus states defined

### 7. Quality

Delegate to tuimm_subagent_sonar:
- Component-specific issues
- Coverage, complexity

### 8. Output

Present results using the ds-component-check template. Follow it EXACTLY — LAST STEP, nothing after this.
