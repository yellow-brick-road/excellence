# Practice: Testing Philosophy

## Guild Position

> We measure test quality, not test quantity. Coverage thresholds are a floor (prevents zero-test repos), not a ceiling. The real metric is: does every acceptance criterion have a corresponding test?

## The Problem

- 80% coverage with shallow tests gives false confidence
- Tests coupled to implementation break on every refactor
- Teams spend more time maintaining tests than writing features
- "Write more tests" is not a strategy — it's noise

## The Principle

**Test behavior, not implementation.**

A test is valuable when it validates something a user or product owner would recognize as meaningful. A test is waste when it only verifies internal wiring that could change without affecting outcomes.

```
❌  expect(wrapper.vm.internalRef).toBe('foo')
✅  expect(screen.getByText('Booking confirmed')).toBeVisible()

❌  expect(composable.isLoading.value).toBe(true)
✅  expect(result.data).toEqual(expectedBooking)

❌  expect(store.$state.items).toHaveLength(3)
✅  expect(store.totalPrice).toBe(29.99)
```

## Selective TDD

Not everything deserves TDD. Apply it where it adds design value:

| File Type | TDD? | Reasoning |
|-----------|------|-----------|
| Utility / Helper | **Yes** — always | Pure functions. Input → output. TDD is perfect here |
| Composable (logic-heavy) | **Yes** | Business logic benefits from test-first design |
| Store (actions/getters) | **Yes** | State transitions are behavioral contracts |
| Component (interactive) | **Alongside** | Write behavior tests with the component, not before |
| Component (presentational) | **No** | Props in, markup out. Test only if complex conditional rendering |
| Page | **No** — integration after | Test key flows after implementation |
| Middleware / Plugin | **Case by case** | TDD if branching logic, skip if just registration |
| Config / Static | **No** | Validation tests if needed, not TDD |

## File Type Testing Strategy

Framework-agnostic. Applies to any frontend stack (Vue, React, Svelte, vanilla).

### Components (Interactive)

Test the user-facing contract: given props + user interaction → visible outcome + emitted events.

**Test:**
- User interactions produce correct outcomes (click, input, submit)
- Props contract (required props, edge values, defaults)
- Emitted events with correct payloads
- Conditional rendering based on state
- Accessibility (keyboard navigation, ARIA attributes, focus management)
- Error states and loading states

**Don't test:**
- Internal refs or reactive state
- CSS classes or DOM structure
- Snapshot of HTML output
- Computed properties that just format strings
- Lifecycle hook side effects (test the outcome instead)

### Components (Presentational)

Mostly skip. Test only if there's meaningful conditional logic.

**Test:**
- Complex conditional rendering (`v-if` / ternary chains with business logic)
- Slot content rendering when behavior depends on it

**Don't test:**
- Static markup
- Styling
- Simple prop-to-text rendering

### Composables / Hooks

Test the input → output contract and side effects.

**Test:**
- Return values for given inputs
- Reactivity: when input changes, output updates correctly
- Side effects (API calls, event listeners) — mock the boundary, test the behavior
- Error handling and edge cases
- Cleanup on unmount

**Don't test:**
- Internal intermediate state
- Implementation of reactive primitives
- Framework internals (ref unwrapping, computed caching)

### Stores

Test state transitions and derived data.

**Test:**
- Actions produce correct state changes
- Getters return expected derived values
- Action sequences (add item → remove item → state is empty)
- Error handling in async actions

**Don't test:**
- Store initialization boilerplate
- Subscription mechanics
- Pinia/Redux/Zustand internals

### Pages / Views

Integration-level. Test key user flows, not every detail.

**Test:**
- Route renders the correct page
- Data fetching populates the page
- Navigation guards redirect correctly
- SEO meta tags for critical pages
- Key user journeys (search → select → book → confirm)

**Don't test:**
- Exact DOM structure
- Layout details
- Every component on the page (they have their own tests)

### Utilities / Helpers

Pure TDD. These are pure functions — test everything.

**Test:**
- All input → output combinations
- Edge cases (null, undefined, empty, boundary values)
- Error throwing for invalid inputs
- Type narrowing behavior

### API Layer

Test the contract between frontend and backend.

**Test:**
- Request shape (URL, method, headers, body)
- Response parsing and transformation
- Error handling (network errors, 4xx, 5xx)
- Retry logic if implemented
- Auth token attachment

**Don't test:**
- HTTP library internals (axios, fetch, ofetch)
- Actual network calls in unit tests

### Middleware / Guards

Test branching logic.

**Test:**
- Redirect conditions (unauthenticated → login, unauthorized → 403)
- Pass-through conditions
- Edge cases (expired token, missing role)

**Don't test:**
- Framework registration mechanics
- Middleware ordering (that's integration)

## The Flow: Ticket to Tested Code

```
1. Ticket arrives
   ↓
2. Analyze: what files will this touch?
   ↓
3. Per file type → what tests are needed? (this matrix)
   ↓
4. Write test skeletons FIRST for TDD-eligible files
   (describe what should happen, not how)
   ↓
5. Implement until tests pass
   ↓
6. Write behavior tests for non-TDD files (components, pages)
   ↓
7. Quality check: are tests testing behavior or implementation?
   ↓
8. Review: does every acceptance criterion have a test?
```

## Excellence Integration (Option C — Shared Skills)

Testing knowledge lives as **shared skills**, not a dedicated agent. Multiple agents use the same testing philosophy:

| Agent | Uses Testing Skills For |
|-------|------------------------|
| Excellence Dev | Writing tests during ticket-to-MR workflow (step 4-6) |
| Quality Guardian | Validating test quality during quality checks (step 7) |
| Excellence MR | Reviewing test adequacy during MR review (step 8) |

### Connection to Spec-Driven Dev

The agent's plan (`SPEC_DRIVEN_DEV.md`) includes acceptance criteria before implementation starts. These ACs become explicit test targets — answering "does every AC have a test?" is straightforward when the ACs are written in the plan before coding begins.

Skills to create:
- `skill_testing_philosophy` — this document, the "why"
- `skill_testing_strategy` — the file-type matrix, the "what"
- `skill_testing_patterns` — framework-specific examples, the "how" (one per framework)

## What NOT to Test — The Explicit List

This list saves more time than any testing guide:

- ❌ Framework internals (reactivity system, virtual DOM, hydration)
- ❌ Third-party library behavior (test your usage, not their code)
- ❌ CSS classes, DOM structure, or HTML snapshots
- ❌ Internal reactive state that isn't part of the public API
- ❌ Computed properties that just format or concatenate
- ❌ Lifecycle hooks directly (test their observable effects)
- ❌ Static/presentational components with no logic
- ❌ Configuration files (unless validation logic exists)
- ❌ Type-only code (interfaces, type guards — TypeScript handles this)
- ❌ Boilerplate (store setup, plugin registration, route definitions)

## Coverage Strategy

| Layer | Threshold | Purpose |
|-------|-----------|---------|
| Shared libraries (`@dx/*`, shared packages) | 80% line coverage | High reuse = high risk. Floor stays high |
| Product frontend (app-level code) | 40-60% line coverage | Flexible. Focus on critical paths |
| Utilities / Helpers | 90%+ | Pure functions. No excuse |
| Components | No line target | Measure: % of interactive components with behavior tests |
| Pages | No line target | Measure: % of critical user journeys covered |

The real dashboard:
- **Acceptance criterion coverage**: % of ACs with a corresponding test
- **Behavior test ratio**: behavior tests / total tests (target: >80%)
- **Test maintenance cost**: time spent fixing broken tests after refactors (should trend down)

## Open Questions

- [ ] How to measure "acceptance criterion coverage" automatically? Can Quality Guardian cross-reference Jira ACs with test descriptions?
- [ ] Should Excellence provide a shared test utilities package (`@dx/test-utils`) with common helpers, mocks, and fixtures?
- [ ] How to handle legacy repos with high coverage but low-quality tests? Migration strategy?
- [ ] Should the "what not to test" list be enforced (lint rule? review check?) or advisory?
- [ ] Framework-specific pattern docs: start with Vue/Nuxt only, or also React/vanilla from day one?
- [ ] Review existing idea docs for Nuxt-centrism — Excellence should speak "frontend" first, framework second
