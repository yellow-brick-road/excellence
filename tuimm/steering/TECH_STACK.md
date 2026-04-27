
# Tech Stack

Current TUI Musement frontend technology stack. Loaded by all TUIMM agents.

> Last verified: April 2026

## Current Stack (b2c-tuimusement-frontend, b2c-nuxt-libraries)

### Runtime
- Node.js 22.14.0 (frontend) / 24.13.0 (libraries)
- npm workspaces

### Framework
- Nuxt 4.3.0
- Vue 3.5.27
- TypeScript 5.9.2 (frontend) / 5.9.3 (libraries)
- Pinia 3.0.4 (state management)

### Styling
- Sass/SCSS
- BEM methodology (enforced via Stylelint regex)
- CSS Modules

### Testing

Vitest with `@nuxt/test-utils`:
- Environment: `nuxt` (via `defineVitestProject`)
- DOM: Happy DOM
- Coverage: v8 provider
- Thresholds: 80% (libraries) / 40-80% (frontend)
- Reporters: default, junit, cobertura

### Code Quality

ESLint — different configs per repo:

| Repo | Config |
|------|--------|
| frontend | `@nuxt/eslint-config` + Prettier |
| libraries | `@nuxt/eslint-config` standalone + stylistic |

Stylelint:
- `stylelint-config-standard-scss` + `stylelint-config-recommended-vue/scss`
- BEM pattern enforced
- `hc-` prefix allowed (design system)

Git Hooks: Husky 9.x, lint-staged 16.x, Commitlint

### Build & Dev
- npm workspaces (monorepo), Lerna 9.x (publishing), Docker

### CMS & Content
- Contentful

### Monitoring
- Datadog (APM, RUM, logs)

### Feature Management
- ConfigCat (feature flags), A/B testing

### Internal Packages
- `@dx/b2c-foundation` — base Nuxt layer
- `@dx/*` — various internal packages

## Legacy Stack (b2c-frontend, b2c-tui)

- Node 14 (frontend) / 18-22 (tui)
- Nuxt 2.15.8 / 2.18.1, Vue 2.x / 2.7.16
- Same integrations: Contentful, ConfigCat, Datadog, Docker, BEM

## Backend (Platform)

- Python, PostgreSQL, MongoDB, Kafka
- AWS (S3, Lambda), NGINX, Microservices
