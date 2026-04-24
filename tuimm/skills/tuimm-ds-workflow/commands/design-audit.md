---
name: ds_design-audit
description: "Full design system compliance check. Use when: user says 'design audit', 'design system check', or 'DS compliance'."
---

# Command: $ds_design-audit

Design system compliance check — compare Figma DS with code, detect drift, measure adoption.

## Services

Ask the user which project to audit. If not specified, ask before proceeding.

## Process

### 1. Extract Figma DS

Delegate to tuimm_subagent_figma:
- List design system components (names, variants, props)
- Extract design tokens (colors, spacing, typography, breakpoints)

### 2. Scan Codebase

Search the project for design system component usage:
- Grep for DS-prefixed components (check project conventions for prefix)
- List all component files in shared packages
- Map: Figma component name → code component name

### 3. Detect Drift

For each DS component with both Figma and code versions:
- Compare props (missing, extra, type mismatches)
- Compare CSS values with design tokens (hardcoded values that should use tokens)
- Flag components where code diverges from Figma spec

### 4. Detect Custom Components

Scan for components NOT in the design system:
- Custom components that duplicate DS functionality
- One-off implementations that should be generalized

### 5. Quality Check

Delegate to tuimm_subagent_sonar:
- Code quality of shared DS components
- Coverage, complexity, maintainability

### 6. Adoption Rate

Calculate per project:
- Total component instances in templates
- DS component instances vs custom instances
- Adoption % = DS instances / total instances

### 7. Output

Present results using the ds-design-audit template. Follow it EXACTLY — LAST STEP, nothing after this.
