# Pipeline Optimization

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-04

## The Pain

CI/CD pipelines in TUI frontend projects are slow and over-engineered. Deploying to a development environment requires waiting through the same gauntlet of checks designed for production. The result:

- **Dev deploys take too long** — developers wait 20-40+ minutes to see changes in a dev environment
- **Manual gates add friction** — button clicks between stages that serve no purpose in lower environments
- **Same pipeline for all environments** — no differentiation between dev, staging, and production
- **Over-checking at the wrong stage** — full security scans, exhaustive linting, coverage thresholds, and quality gates run before code even reaches dev
- **Developer frustration** — context switching while waiting, broken flow, reduced iteration speed

This is exactly the kind of cross-cutting friction Excellence exists to eliminate.

## The Principle

> Right checks, right stage, right cost.

Not every check needs to run at every point. The pipeline should be **environment-aware**: the confidence level required to deploy to dev is fundamentally different from production.

- **Dev** — fast feedback, minimal gates. The goal is to see your changes running. You're the only audience
- **Staging** — quality validation. This is where thorough checks earn their keep
- **Production** — full confidence. Security, quality, coverage, approval — everything

## Proposed Model

### Environment-Aware Pipeline Stages

| Check | Dev | Staging | Production |
|-------|-----|---------|------------|
| Build | ✅ | ✅ | ✅ |
| Type check | ✅ | ✅ | ✅ |
| Lint (fast) | ✅ | ✅ | ✅ |
| Unit tests | ⚡ affected only | ✅ full suite | ✅ full suite |
| Coverage thresholds | ❌ | ✅ | ✅ |
| Security scan (SAST) | ❌ | ✅ | ✅ |
| Dependency audit | ❌ | ✅ | ✅ |
| SonarQube quality gate | ❌ | ✅ | ✅ |
| E2E tests | ❌ | ✅ critical paths | ✅ full suite |
| Manual approval gate | ❌ | ❌ | ✅ |
| Docker image build | ✅ (cached) | ✅ | ✅ (immutable tag) |
| Deploy | ✅ auto | ✅ auto | ✅ after approval |

⚡ = optimized/partial run

### Key Changes

1. **Dev deploys should be near-instant** — build, type check, fast lint, deploy. That's it. If it compiles and the types are right, ship it to dev
2. **Tests run smart, not exhaustive** — in dev, only run tests affected by changed files. Full suite in staging+
3. **Security and quality gates move to staging** — these checks protect production, not dev environments
4. **Remove manual gates before dev** — no human should click a button to deploy to a dev environment
5. **Cache aggressively** — Docker layers, node_modules, build artifacts. Every cold start is wasted time

## Analysis Required

Before proposing concrete changes, Excellence needs to audit the current state:

### Phase 1 — Audit

- [ ] Map current `.gitlab-ci.yml` structure across all frontend repos
- [ ] Measure actual pipeline duration per stage (dev, staging, production)
- [ ] Identify which checks run at which stage today
- [ ] Find redundant or duplicate steps
- [ ] Measure cache hit rates (Docker, npm, build artifacts)
- [ ] Compare pipeline configs across repos — how much divergence exists?
- [ ] Talk to developers — what's the actual pain? Where do they wait the most?

### Phase 2 — Propose

- [ ] Define the environment-aware model for TUI frontend repos
- [ ] Identify quick wins (things that can change this week)
- [ ] Identify structural changes (pipeline refactoring, shared CI templates)
- [ ] Estimate time savings per deploy cycle
- [ ] Draft shared `.gitlab-ci.yml` templates or includes

### Phase 3 — Implement

- [ ] Pilot with one repo
- [ ] Measure before/after
- [ ] Roll out to remaining repos
- [ ] Create shared CI templates in a dedicated repo (or `@dx/ci-templates`)

## Quick Wins (Likely)

These are common patterns that almost always help — to be validated during audit:

- **Parallel stages** — run lint, type check, and tests concurrently instead of sequentially
- **Skip redundant Docker builds** — if the image hasn't changed, don't rebuild it
- **Affected-only test runs** — use Vitest's `--changed` flag for dev pipelines
- **Remove manual gates for dev** — auto-deploy on merge to feature branches
- **Shared CI includes** — stop copy-pasting pipeline configs across repos

## Connection to Excellence

This is textbook Excellence scope:

- **Cross-cutting problem** — affects all frontend repos, not one vertical
- **Reusable solution** — shared CI templates, not per-team fixes
- **Measurable impact** — pipeline duration is a hard number, easy to track before/after
- **Developer productivity** — directly reduces friction and wait time
- **No product ownership needed** — this is infrastructure, not features

### KPI

- Pipeline duration (dev deploy): target < 5 minutes
- Pipeline duration (staging full): target < 15 minutes
- Developer wait time per deploy cycle
- Number of manual gates per environment

## Open Questions

- [ ] Who owns the pipeline configs today? DevOps team, each vertical, or shared?
- [ ] Are there compliance requirements forcing certain checks in all environments?
- [ ] Is there appetite for shared CI templates, or do teams want autonomy?
- [ ] What's the current Docker build strategy? Multi-stage? Layer caching?
- [ ] Are there existing GitLab CI includes or templates being used?
