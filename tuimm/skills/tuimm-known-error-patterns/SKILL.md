---
name: tuimm-known-error-patterns
description: |
  Catalog of known production error patterns for TUI Musement frontend services.
  Use when: running obs_dd-scan or datadog-scan, classifying errors, writing Datadog queries.
  Contains: error patterns with exact Datadog queries, severity baselines, and context.
---

# Known Error Patterns

Catalog of recurring production errors. Use to classify scan results and avoid re-investigating known issues.

Last updated from real scan: 2026-04-13

## Datadog Field Reference

| Field | Use for | Valid for groupBy |
|-------|---------|:-----------------:|
| `@error.message` | Primary error text | ✅ |
| `@error.kind` | Error type (TypeError, RangeError...) | ✅ |
| `@error.stack` | Stack trace | ❌ |
| `@error.data.context` | Custom context string | ❌ |
| `@http.url` | Request URL | ✅ |
| `@view.url` | Page URL | ✅ |
| `@http.status_code` | HTTP status | ✅ |
| `message` | Log message (NOT a facet) | ❌ |

## API Limitations

- `aggregate-logs` groupBy returns max 10 results (fixed, cannot increase)
- Do NOT add `sort` or `limit` to groupBy — causes API failure
- `message` is NOT a valid facet for groupBy — use `@error.message`
- `search_logs` returns 10 most recent logs — no temporal diversity

## Patterns

### Infrastructure / Framework

| Pattern | Query | Severity | Notes |
|---------|-------|----------|-------|
| Nuxt app manifest fetch | `@error.message:*_nuxt/builds/meta*` | LOW | Normal during deploys, transient |
| Hydration mismatch | `@error.message:"Hydration completed but contains mismatches"` | LOW | SSR/client drift, usually cosmetic |
| NITRO SERVER ERROR 404 | `message:"NITRO SERVER ERROR" @error.statusCode:404` | MEDIUM | Missing routes or stale URLs |

### Application Bugs

| Pattern | Query | Severity | Notes |
|---------|-------|----------|-------|
| Vue Router infinite loop | `@error.kind:RangeError @error.message:"Maximum call stack size exceeded"` | CRITICAL | Recursive navigation guard or computed |
| Z._endPatch TypeError | `@error.message:*_endPatch*` | HIGH | Vue internal — likely reactivity bug |
| Component names in URL (404) | `@error.message:*tui-activity-gallery-image* OR @error.message:*activity-card-imgix* OR @error.message:*imageWithLazyLoading*` | HIGH | Component name leaking into URL — bug |
| undefined srcset in URL | `@error.message:*undefined 1x*` | HIGH | Image source not resolved — bug |

### External Services

| Pattern | Query | Severity | Notes |
|---------|-------|----------|-------|
| Slug service failure | `@error.message:*slug-service-cf.prod.musement.com*` | MEDIUM | Backend dependency |
| SSO Communication Timeout | `@error.message:*SSO Communication Timeout*` | MEDIUM | Auth provider latency |
| Third-party XHR failures | `@http.url:(riskified.com OR contentful.com OR smct.io OR adn.cloud) @http.status_code:0` | LOW | Usually bots, not real users |

### SEO / Content

| Pattern | Query | Severity | Notes |
|---------|-------|----------|-------|
| Activity not available | `@error.data.context:"Activity not available"` | LOW | Missing lang/market combo — SEO crawlers |

### Bot-specific

| Pattern | Query | Severity | Notes |
|---------|-------|----------|-------|
| Cookie banner crash | `@error.message:"Object.defineProperty called on non-object" @error.stack:*msm-cookie-banner*` | LOW | Only in HeadlessChrome/bots |
