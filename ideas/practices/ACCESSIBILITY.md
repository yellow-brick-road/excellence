# Accessibility Standards

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-04

## The Pain

Accessibility is inconsistent across TUI frontend projects. Some teams make an effort, most don't, and there's no shared standard or tooling. The risk is both ethical (users with disabilities can't use the product) and regulatory (European Accessibility Act, WCAG compliance).

A full org-wide accessibility audit is a massive undertaking. We're not doing that.

## The Principle

> New shared components ship accessible. Existing code improves incrementally through wrappers and directives.

Don't boil the ocean. Make the default path the accessible path.

## Proposed Approach

### 1. Accessible-by-Default Shared Library

All new components in the shared Nuxt module (see REPO_STRATEGY.md) ship with:

- **WAI-ARIA attributes** — roles, labels, states, properties
- **Keyboard navigation** — focusable, operable without mouse
- **Semantic HTML** — correct elements, heading hierarchy, landmarks
- **Screen reader support** — meaningful alt text, live regions where needed

This is not optional. If a component goes into the shared library, it meets these requirements.

### 2. Wrapper Components & Directives

For existing code that can't be rewritten, provide:

- **Wrapper components** — e.g., `<AccessibleModal>` wraps any modal with focus trap, escape handling, aria-modal, role="dialog"
- **Vue directives** — e.g., `v-aria-label`, `v-focus-trap`, `v-announce` (live region announcements)
- **Composables** — e.g., `useKeyboardNavigation()`, `useFocusTrap()`, `useAnnounce()`

Teams can adopt these incrementally without rewriting their components.

### 3. Minimum Standard

Target: **WCAG 2.1 Level AA** for shared library components.

For team-owned components: recommended, not enforced. Excellence provides the tools, teams decide adoption pace.

### What We Provide

| Asset | Description |
|-------|-------------|
| Accessible shared components | Library components with built-in a11y |
| Wrapper components | Drop-in a11y wrappers for common patterns (modals, dropdowns, tabs) |
| Vue directives | `v-focus-trap`, `v-aria-label`, etc. |
| Composables | `useKeyboardNavigation()`, `useFocusTrap()`, `useAnnounce()` |
| ESLint plugin | `eslint-plugin-vuejs-accessibility` in shared config |
| CI check (optional) | axe-core in Vitest for component-level a11y testing |

### What We Don't Do

- ❌ Full audit of all existing pages
- ❌ Mandate WCAG compliance for legacy code
- ❌ Block deploys for a11y issues (yet)
- ❌ Become the a11y police

## Analysis Required

- [ ] Survey current a11y state in key user flows (booking, search, checkout)
- [ ] Identify the most common a11y violations (likely: missing labels, no keyboard nav, no focus management)
- [ ] Evaluate `eslint-plugin-vuejs-accessibility` for shared ESLint config
- [ ] Evaluate axe-core integration with Vitest
- [ ] Define the first batch of wrapper components (modals, dropdowns, tabs, accordions)

## Connection to Excellence

- Shared library is the vehicle — a11y comes built-in, not bolted on
- Wrappers and directives let teams improve without rewriting
- ESLint plugin catches issues at dev time, not in production
- Regulatory compliance (European Accessibility Act) makes this a business need, not just a nice-to-have
- Connects to Design System agent — Figma ↔ code alignment should include a11y properties
