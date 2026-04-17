# Commands

Executable workflows that agents follow step by step. Each command defines: what inputs it needs, what to do, which subagents to call, and which template to use for output.

## How they work

When a user types `$dev_solve DIS-1234`, the agent:
1. Reads `commands/dev_solve.md`
2. Follows the steps defined inside
3. Delegates API calls to subagents (Jira, GitLab, etc.)
4. Formats the output using the referenced template

## Naming convention

Commands are prefixed by domain:

| Prefix | Agent | Examples |
|--------|-------|---------|
| `dev_` | Dev | `dev_solve`, `dev_continue`, `dev_implement` |
| `mr_` | MR | `mr_review`, `mr_list`, `mr_approve`, `mr_rebase`, `mr_comments` |
| `obs_` | Observability | `obs_dd-scan`, `obs_dd-investigate` |
| `qg_` | Quality Guardian | `qg_quality-check`, `qg_dependency-scan`, `qg_release`, `qg_security-scan` |
| `devex_` | DevEx | `devex_flag-cleanup`, `devex_i18n-coverage`, `devex_content-audit` |
| `ds_` | Design System | `ds_component-check`, `ds_design-audit` |
| `kn_` | Knowledge | `kn_doc-health`, `kn_runbook`, `kn_onboarding` |
| `planner_` | Planner | `planner_design`, `planner_analyze`, `planner_decompose` |
| `jira_` | Shared (all agents) | `jira_create-ticket`, `jira_edit-ticket`, `jira_comment-ticket` |
| `weblate_` | Shared (Dev, MR, DevEx, DS) | `weblate_add-key`, `weblate_validate`, `weblate_coverage` |
| — | Meta | `get-commands` |

## How they load

Each agent loads only its own commands via `skill://` globs in the agent JSON:

```json
{
  "resources": [
    { "type": "skill", "path": "~/.kiro/tuimm/commands/dev_*.md" },
    { "type": "skill", "path": "~/.kiro/tuimm/commands/jira_*.md" }
  ]
}
```

Commands are loaded on-demand (not at startup like steering). The agent reads the file when the user triggers the command.
