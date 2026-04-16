---
name: get-commands-output
description: "Output format for $get-commands. Use when: formatting the command listing response. Contains: section layout, agent grouping, shared command notation."
---

TUIMM commands
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TUIMM Default (this agent):
- $get-commands: List all available commands
- No domain commands — swap to a specialist agent below

TUIMM Dev:
- $dev_solve: Solve a Jira ticket end-to-end
- $dev_implement: Implement from description
- $dev_continue: Continue work in progress
- + shared (jira + weblate)

TUIMM MR:
- $mr_review: Review a merge request
- $mr_comments: Address review comments
- $mr_approve: Approve a merge request
- $mr_rebase: Rebase a merge request
- $mr_list: List open MRs across repos
- + shared (jira + weblate)

TUIMM Quality Guardian:
- $qg_quality-check: SonarQube quality gate and issues
- $qg_tech-debt-report: Tech debt metrics and hotspots
- $qg_dependency-review: Evaluate Renovate/Dependabot MRs
- $qg_dependency-scan: Proactive dependency update scan
- $qg_release: Changelog, version bump, publish
- $qg_security-scan: Preflight-sast security findings analysis
- $qg_generate-guidelines: Extract coding guidelines from project code
- + shared (jira)

TUIMM Observability:
- $obs_dd-scan: Scan production errors
- $obs_dd-investigate: Investigate a specific error
- + shared (jira)

TUIMM DevEx:
- $devex_flag-cleanup: Find stale/orphan feature flags
- $devex_i18n-coverage: Scan code for missing translations
- $devex_content-audit: Contentful model and content audit
- + shared (jira + weblate)

TUIMM Design System:
- $ds_design-audit: Figma ↔ codebase drift analysis
- $ds_component-check: Compare Figma spec vs code implementation
- + shared (jira + weblate)

TUIMM Knowledge:
- $kn_doc-health: Confluence documentation health check
- $kn_runbook: Generate or update a runbook
- $kn_onboarding: Generate onboarding guide
- + shared (jira)

TUIMM Planner:
- $planner_analyze: Analyze requirement and recommend approach
- $planner_design: Produce technical design document
- $planner_decompose: Break design into autobuild-compatible tasks
- + shared (jira)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
36 commands total (10 domain prefixes + 1 meta) across 9 agents

Adapt "(this agent)" to whichever agent runs the command. Show "Your commands" first when run from a non-default agent. "shared (jira)" = $jira_create-ticket + $jira_edit-ticket + $jira_comment-ticket. "shared (jira + weblate)" = jira shared + $weblate_add-key + $weblate_validate + $weblate_coverage + $weblate_translate-missing.

RULES: This is the COMPLETE output. Do NOT add commentary or follow-up questions after the listing.
