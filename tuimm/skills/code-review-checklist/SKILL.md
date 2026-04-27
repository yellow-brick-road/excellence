---
name: code-review-checklist
description: |
  Pre-commit code review checklist — what to verify before committing changes.
  Use when: reviewing code changes, running pre-commit checks, or analyzing staged diffs.
  Contains: critical checks (broken imports, removed functions, changed signatures),
  concurrency checks, and quality checks ordered by severity.
---

# Code Review Checklist

Ordered by severity. Check top-down — stop and report as soon as a CRITICAL is found.

## 🔴 CRITICAL — Will break the build or other code

### Broken imports

For every file that was renamed, moved, or deleted:
- Search the entire codebase for imports referencing the old path
- Check barrel files (`index.ts`) that re-export from the changed file
- Check dynamic imports (`import()`) and lazy routes
- Check test files that import from the changed module

```
# Find all references to a deleted/moved file
grep -r "from.*old-file-name" --include="*.ts" --include="*.vue"
```

### Removed exports / functions / types

For every function, class, type, or constant that was removed or renamed:
- Search the entire codebase for usages
- Check if it's exported from a barrel file
- Check if it's used in tests
- Check if it's part of a public API (shared library)

```
# Find all usages of a removed symbol
grep -r "symbolName" --include="*.ts" --include="*.vue" --include="*.spec.ts"
```

### Changed function signatures

For every function whose parameters changed (added, removed, reordered, type changed):
- Find ALL call sites across the codebase
- Verify each call site passes the correct arguments
- Check if the function is part of a public API — breaking change?
- Check default values — does removing a default break existing callers?

### Changed prop interfaces

For every Vue component whose props changed:
- Find ALL usages of the component across templates and JSX
- Verify each usage passes the correct props
- Check if required props were added — all parents must provide them
- Check if prop types changed — all parents must pass the correct type

### Removed CSS classes

For every CSS class that was removed or renamed:
- Search templates, JSX, and dynamic class bindings
- Check if the class is used in other components
- Check test selectors that reference the class

## 🟠 HIGH — Will cause runtime errors or data issues

### Race conditions and async issues

- `await` missing on async calls — fire-and-forget that should wait
- State mutations after `await` — component might be unmounted
- Shared mutable state accessed from multiple async flows
- Missing cleanup in `onUnmounted` for timers, subscriptions, event listeners
- `Promise.all` where one rejection should not cancel others (use `Promise.allSettled`)

### Null/undefined access

- Optional chaining (`?.`) missing where data could be null
- Array access without bounds check
- Object destructuring without defaults on optional fields
- API response fields assumed to always exist

### Error handling

- `try/catch` missing around external calls (API, file system, third-party libs)
- Catch blocks that swallow errors silently (`catch (e) {}`)
- Unhandled promise rejections (missing `.catch()` or `try/catch` on `await`)
- Error boundaries missing for component trees that fetch data

### Type safety

- `any` casts that bypass type checking
- Type assertions (`as Type`) without runtime validation
- Generic types used without constraints
- Union types not narrowed before access

## 🟡 MEDIUM — Quality and maintainability

### Dead code

- Unused imports (check after all other changes)
- Unused variables and functions
- Commented-out code blocks (should be removed, not commented)
- Unreachable code after return/throw

### Performance

- Unnecessary re-renders (missing `computed`, reactive deps too broad)
- Missing `key` on `v-for` items
- Large objects in reactive state that should be `shallowRef`
- N+1 patterns in data fetching (loop of API calls)
- Missing debounce/throttle on frequent events (scroll, resize, input)

### Accessibility

- Interactive elements without keyboard support
- Missing `aria-label` on icon-only buttons
- Missing `alt` on images
- Color as the only indicator (needs text/icon too)
- Focus management after dynamic content changes

### Naming and conventions

- Check against loaded skills (BEM, component naming, file naming)
- Consistent naming within the file
- Descriptive variable names (no `data`, `temp`, `x`)

## ⚪ LOW — Style and preferences

- Import ordering
- Trailing commas consistency
- Line length
- Comment quality (outdated comments worse than no comments)

## Process

1. Run through CRITICAL checks first — use `code` tool (pattern_search, search_symbols) and `shell` (grep, find) for codebase-wide search
2. If any CRITICAL found: stop, report immediately, recommend "fix before commit"
3. Continue with HIGH, MEDIUM, LOW
4. For each finding: file, line, severity, what's wrong, how to fix
5. Summary: X critical, Y high, Z medium — proceed or fix first
