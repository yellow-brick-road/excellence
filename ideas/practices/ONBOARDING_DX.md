# Onboarding Developer Experience

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-04

## The Pain

A new developer joining a TUI frontend team faces an unpredictable setup experience. Every repo has:

- Different README quality (some excellent, some nonexistent)
- Different environment variable requirements
- Different Docker configurations
- Different local setup steps
- Different tooling assumptions

Time from `git clone` to running application varies wildly. Some repos take 10 minutes, others take a full day with Slack messages asking "how do I run this?"

This is wasted time that compounds: every new joiner, every team rotation, every developer picking up an unfamiliar repo.

## The Principle

> A developer should go from zero to running app in under 15 minutes, in any frontend repo.

## Proposed Model

### 1. Standardized README Template

Every frontend repo gets a README with consistent sections:

- **Prerequisites** — Node version, Docker, required global tools
- **Quick Start** — copy-paste commands to get running (max 3 steps)
- **Environment Variables** — table with name, description, where to get it, example value
- **Available Scripts** — what `npm run dev`, `npm run test`, etc. do
- **Architecture** — brief overview of project structure
- **Troubleshooting** — common setup issues and fixes

### 2. Consistent Setup Flow

Standardize across repos:

```bash
git clone <repo>
cp .env.example .env    # all repos provide .env.example
npm install
npm run dev
```

No repo should require more than this for basic local development. If it does, the extra steps should be automated or documented in Quick Start.

### 3. TUI CLI Integration

`tui fe init` could automate the setup:

- Detect repo type (Nuxt, library, legacy)
- Check prerequisites (Node version, Docker)
- Copy env template
- Install dependencies
- Run health check
- Report status

### 4. `.env.example` as Contract

Every repo maintains a `.env.example` with:

- All required variables (with placeholder values)
- Comments explaining each variable
- Grouped by service (Contentful, ConfigCat, Datadog, etc.)

No secret values — just the shape. Actual values come from team onboarding or a shared vault.

## Analysis Required

### Phase 1 — Audit

- [ ] Survey current README quality across frontend repos
- [ ] Measure actual "time to first run" for 3-5 key repos
- [ ] Identify the most common setup blockers (missing env vars, Docker issues, Node version mismatches)
- [ ] Check which repos have `.env.example` and which don't

### Phase 2 — Standardize

- [ ] Create README template
- [ ] Create `.env.example` template
- [ ] Define the "15-minute setup" contract
- [ ] Add `tui fe init` to TUI CLI scope

### Phase 3 — Roll Out

- [ ] Apply to main repos (b2c-tuimusement-frontend, b2c-nuxt-libraries first)
- [ ] Provide migration guide for other repos
- [ ] Track adoption

## KPIs

- Time to first successful `npm run dev` (target: < 15 minutes)
- Percentage of repos with standardized README
- Percentage of repos with `.env.example`
- New developer satisfaction (survey)

## Connection to Excellence

- Cross-cutting: affects every repo, every team, every new joiner
- Reusable: one template, N repos
- Measurable: time to first run is a hard number
- Low friction: README template is easy to adopt, no architectural changes needed
- TUI CLI integration: `tui fe init` makes it automated, not just documented
