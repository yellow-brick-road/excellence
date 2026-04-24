# Artifacts

Reference for all agent artifacts. Update this file each time a new command, prompt, or template is created.

## Artifact Types

| Type | Location | Loading | Purpose |
|------|----------|---------|---------|
| Skill | `tuimm/skills/` | Loaded via `skill://.../skills/**/SKILL.md` in agent JSON | Self-contained knowledge + commands + templates (agentskills.io pattern) |
| Command | `tuimm/skills/*/commands/` | Part of skill — loaded when skill activates | Single-agent or shared targeted actions |
| Template | `tuimm/skills/*/assets/templates/` | Part of skill — referenced by commands | Output format definitions |
| Steering | `tuimm/steering/` | Loaded via `file://` glob at startup | Shared behavioral rules (transversal, not per-skill) |
| Prompt | `tuimm/prompts/` | Preloaded as agent resource | Multi-domain workflows |
| Tool | `tuimm/tools/` | Executed via `bash` from commands | Shell scripts and utilities for API queries and automation |

## Command Execution Rules

- `$exact-name` → execute the command immediately (already loaded as skill)
- Similar input (e.g. "scan", "morning") → ask: "Do you want to run $command-name?"
- `$commands` → list all available commands with descriptions

## Command Prefixes

| Prefix | Owner | Loaded by |
|--------|-------|-----------|
| `dev_` | tuimm_dev | tuimm_dev only |
| `mr_` | tuimm_mr | tuimm_mr only |
| `obs_` | tuimm_observability | tuimm_observability only |
| `qg_` | tuimm_quality_guardian | tuimm_quality_guardian only |
| `devex_` | tuimm_devex | tuimm_devex only |
| `ds_` | tuimm_design_system | tuimm_design_system only |
| `kn_` | tuimm_knowledge | tuimm_knowledge only |
| `planner_` | tuimm_planner | tuimm_planner only |
| `weblate_` | shared | dev, mr, devex, design_system |
| `jira_` | shared | dev, mr, obs, qg, devex, ds, knowledge, planner |

## Output

Reports save to `outputs/YYYY-MM-DD_HHmm_NAME.md`

## Commands by Agent

### TUIMM Default (1)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$get-commands` | "what commands", "list commands", "capabilities" | List all available commands across agents |

### TUIMM Dev (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$dev_solve` | "solve [TICKET-ID]" | Full task-to-MR workflow |
| `$dev_implement` | "implement [description]" | Ad-hoc implementation without Jira ticket |
| `$dev_continue` | "continue", "resume" | Resume interrupted workflow |

### TUIMM MR (5)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$mr_review` | "review [MR-ID]" | Full MR review with structured feedback |
| `$mr_comments` | "comments [MR-ID]" | Address review comments on your MR |
| `$mr_approve` | "approve [MR-ID]" | Approve a merge request |
| `$mr_rebase` | "rebase [MR-ID]" | Rebase MR on target branch via API |
| `$mr_list` | "list", "my MRs" | Cross-repo MR briefing |

### TUIMM Observability (2)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$obs_dd-scan` | "scan", "morning scan" | Production error scan (Datadog) |
| `$obs_dd-investigate` | "investigate [error]" | Deep root cause analysis (Datadog) |

### Jira — shared (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$jira_create-ticket` | "create ticket", "new ticket" | Create a Jira ticket with structured template |
| `$jira_edit-ticket` | "edit ticket [KEY]" | Edit an existing Jira ticket |
| `$jira_comment-ticket` | "comment on [KEY]" | Add a comment to a Jira ticket |

### Weblate — shared (4)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$weblate_add-key` | "add translation key" | Add key to module, draft MR |
| `$weblate_validate` | "validate translations" | Check XLIFF structure and consistency |
| `$weblate_coverage` | "translation coverage" | Coverage report per module/locale |
| `$weblate_translate-missing` | "translate missing keys" | LLM-proposed translations, draft MR |

### TUIMM Quality Guardian (7)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$qg_quality-check` | "quality check", "quality scan" | Full quality scan across projects |
| `$qg_tech-debt-report` | "tech debt", "debt report" | Debt quantification, hotspots, ROI analysis |
| `$qg_dependency-review` | "dependency review", "renovate" | Reactive Renovate MR triage |
| `$qg_dependency-scan` | "scan dependencies", "check updates" | Proactive dependency analysis |
| `$qg_release` | "$release", "$release [pkg]" | Analyze changes, propose version, publish |
| `$qg_security-scan` | "security scan [MR]", "preflight [MR]" | Preflight-sast findings analysis for MR pipelines |
| `$qg_generate-guidelines` | "generate guidelines", "extract guidelines" | Extract coding guidelines from project code |

### TUIMM DevEx (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$devex_flag-cleanup` | "flag cleanup", "stale flags" | Stale flag detection, cleanup plan |
| `$devex_i18n-coverage` | "i18n coverage", "translation audit" | Codebase-level i18n analysis |
| `$devex_content-audit` | "content audit", "contentful check" | Content model health, environment drift |

### TUIMM Design System (2)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$ds_design-audit` | "design audit", "DS compliance" | Design system compliance check |
| `$ds_component-check` | "component check [name]" | Compare Figma spec vs code implementation |

### TUIMM Knowledge (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$kn_doc-health` | "doc health", "docs audit" | Documentation health audit |
| `$kn_runbook` | "runbook [topic]" | Generate runbook from existing knowledge |
| `$kn_onboarding` | "onboarding [team]" | Personalized onboarding guide |

### TUIMM Planner (3)

| Command | Trigger | Description |
|---------|---------|-------------|
| `$planner_analyze` | "analyze [requirement]" | Determine planning level (0-3) |
| `$planner_design` | "design [topic]", "plan [topic]" | Technical design with specialist consultation |
| `$planner_decompose` | "decompose", "break into tasks" | Autobuild-compatible task files |

## Prompts

(none yet)

## Templates

| Template | Used by | Description |
|----------|---------|-------------|
| `jira-ticket.md` | `$jira_create-ticket`, `$jira_edit-ticket` | Jira ticket structure |
| `jira-comment.md` | `$jira_comment-ticket` | Comment posted confirmation |
| `get-commands-output.md` | `$get-commands` | Output format for listing available commands |
| `dev-solve.md` | `$dev_solve`, `$dev_implement` | Implementation completion summary |
| `dev-continue.md` | `$dev_continue` | Workflow resume status |
| `mr-review-summary.md` | `$mr_review` | MR review summary with findings, quality gate, recommendation |
| `mr-list-summary.md` | `$mr_list` | MR briefing output with sections by urgency |
| `mr-approve.md` | `$mr_approve` | Approval confirmation |
| `mr-rebase.md` | `$mr_rebase` | Rebase confirmation |
| `mr-comment-item.md` | `$mr_comments` | Per-comment presentation with code and actions |
| `mr-comments-summary.md` | `$mr_comments` | Final summary after all comments processed |
| `obs-scan-summary.md` | `$obs_dd-scan` | Scan output with users/bots sections, severity, status |
| `obs-investigate.md` | `$obs_dd-investigate` | Investigation report with root cause analysis |
| `qg-quality-check.md` | `$qg_quality-check` | Quality scan report |
| `qg-dependency-review.md` | `$qg_dependency-review` | Renovate MR triage report |
| `qg-dependency-scan.md` | `$qg_dependency-scan` | Proactive dependency scan report |
| `qg-release.md` | `$qg_release` | Release proposal with changelog |
| `qg-tech-debt-report.md` | `$qg_tech-debt-report` | Tech debt analysis report |
| `qg-security-scan.md` | `$qg_security-scan`, `$mr_review` | Preflight-sast SAST/SBOM findings report |
| `qg-generate-guidelines.md` | `$qg_generate-guidelines` | Guidelines extraction results |
| `guidelines-generator/extract.md` | `$qg_generate-guidelines` | Extraction prompt template for guidelines-generator tool |
| `devex-content-audit.md` | `$devex_content-audit` | Contentful health check report |
| `devex-flag-cleanup.md` | `$devex_flag-cleanup` | Stale flags cleanup report |
| `devex-i18n-coverage.md` | `$devex_i18n-coverage` | Codebase i18n analysis report |
| `ds-component-check.md` | `$ds_component-check` | Figma vs code comparison report |
| `ds-design-audit.md` | `$ds_design-audit` | Design system compliance report |
| `kn-doc-health.md` | `$kn_doc-health` | Documentation health report |
| `kn-onboarding.md` | `$kn_onboarding` | Onboarding guide creation confirmation |
| `kn-runbook.md` | `$kn_runbook` | Runbook creation confirmation |
| `planner-analyze.md` | `$planner_analyze` | Requirement analysis report |
| `planner-decompose.md` | `$planner_decompose` | Task decomposition summary |
| `planner-design.md` | `$planner_design` | Technical design document format |
| `weblate-add-key.md` | `$weblate_add-key` | Translation key addition confirmation |
| `weblate-coverage.md` | `$weblate_coverage` | Translation coverage report |
| `weblate-translate-missing.md` | `$weblate_translate-missing` | Missing translations completion confirmation |
| `weblate-validate.md` | `$weblate_validate` | XLIFF validation report |
| `template-blueprint.md` | — | Reference structure for creating new templates |

## Skills

| Skill | Used by | Description |
|-------|---------|-------------|
| `commit-conventions` | GitLab subagent, Code Reviewer | Commit format, types, scope, process |
| `gitlab-conventions` | GitLab subagent, Code Reviewer | MR templates, thread rules, query limits |
| `jira-adf` | Jira subagent, Confluence subagent | ADF format for description/comment fields |
| `weblate-conventions` | Weblate commands | Repo URL, module discovery, XLIFF tooling |
| `code-review-checklist` | Code Reviewer | Pre-commit checklist by severity |
| `workspace-mcp` | Dev, MR, Default | Workspace MCP config pattern for Nuxt projects |
| `file-modifier` | Dev, MR, any agent with write access | File modification conventions (lint/format order) |
| `mcp-tools-reference` | Code Reviewer, any agent needing MCP config | Read vs write tool classification per MCP server |
| `known-error-patterns` | Observability, `$obs_dd-scan` | Known production error patterns with Datadog queries and severity baselines |
| `jira-context-gathering` | Jira commands, Dev commands | Full ticket context checklist — what to fetch and how to query the subagent |
| `security-preflight` | `$qg_security-scan`, `$mr_review` | Preflight-sast extraction procedure — find job, parse JUnit, classify SAST/SBOM |

## Tools

| Tool | Used by | Description |
|------|---------|-------------|
| `gitlab-list-mrs.py` | `$mr_list` | Cross-repo MR listing — personal + bot MRs, auto-discovers projects via API |
| `workspace-cleanup-check.py` | Session start (bg) | Scans temp workspaces, checks GitLab for merged/closed MRs and branches |
