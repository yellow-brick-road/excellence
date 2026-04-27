---
name: tuimm-qg-workflow
description: Quality Guardian workflow commands for code quality, tech debt, dependencies, releases, and security scanning. Use when checking quality gates, managing debt, reviewing dependencies, or releasing packages.
---

# Quality Guardian Workflow

Commands for the tuimm_quality_guardian agent: quality checks, tech debt, dependency health, releases, and security.

## Available Commands

- `$qg_quality-check` — "quality check", "quality scan" — Full quality scan across projects. Read the command from [commands/quality-check.md](commands/quality-check.md)
- `$qg_tech-debt-report` — "tech debt", "debt report" — Technical debt analysis. Read the command from [commands/tech-debt-report.md](commands/tech-debt-report.md)
- `$qg_dependency-review` — "dependency review", "renovate" — Triage Renovate Bot MRs. Read the command from [commands/dependency-review.md](commands/dependency-review.md)
- `$qg_dependency-scan` — "scan dependencies", "check updates" — Proactive dependency scanning. Read the command from [commands/dependency-scan.md](commands/dependency-scan.md)
- `$qg_release` — "$release", "$release [package]" — Release management workflow. Read the command from [commands/release.md](commands/release.md)
- `$qg_security-scan` — "security scan [MR]", "preflight [MR]" — Security preflight scan. Read the command from [commands/security-scan.md](commands/security-scan.md)

## Templates

- [assets/templates/qg-quality-check.md](assets/templates/qg-quality-check.md)
- [assets/templates/qg-tech-debt-report.md](assets/templates/qg-tech-debt-report.md)
- [assets/templates/qg-dependency-review.md](assets/templates/qg-dependency-review.md)
- [assets/templates/qg-dependency-scan.md](assets/templates/qg-dependency-scan.md)
- [assets/templates/qg-release.md](assets/templates/qg-release.md)
- [assets/templates/qg-security-scan.md](assets/templates/qg-security-scan.md)
- [assets/templates/template-blueprint.md](assets/templates/template-blueprint.md) — Blueprint for creating new templates
