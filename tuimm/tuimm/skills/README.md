# Skills

Knowledge documents that agents consult when they need specific expertise. Not executable — they're reference material that agents read before acting.

## How they work

When an agent needs to create a Jira ticket, it reads `skills/jira-adf/SKILL.md` to understand Atlassian Document Format. When it needs to commit code, it reads `skills/commit-conventions/SKILL.md` for the format rules. The agent decides when to consult a skill based on the task.

## Skills

| Skill | Used by | What it contains |
|-------|---------|------------------|
| `commit-conventions` | GitLab subagent, Code Reviewer | Commit format, types, scope rules |
| `gitlab-conventions` | GitLab subagent, Code Reviewer | MR templates, thread rules, API limits |
| `jira-adf` | Jira subagent, Confluence subagent | Atlassian Document Format for descriptions |
| `jira-context-gathering` | Dev, Planner | Full ticket context checklist — what to fetch |
| `weblate-conventions` | Weblate commands | Repo URL, module discovery, XLIFF format |
| `code-review-checklist` | Code Reviewer | Pre-commit checklist ordered by severity |
| `file-modifier` | Dev, MR | Lint/format order after file changes |
| `workspace-mcp` | Dev, MR, Default | nuxt-mcp-dev workspace config pattern |
| `mcp-tools-reference` | Code Reviewer | Read vs write tool classification per MCP |
| `known-error-patterns` | Observability | Recurring production errors with Datadog queries |
| `security-preflight` | Quality Guardian, MR | How to extract preflight-sast findings |
| `autobuild-reference` | Planner | Task engine CLI, task file format |
| `bg-reference` | Background tools | Background execution library API |
| `logd-reference` | Observability, autobuild | Log daemon and client library API |

## Structure

Each skill is a directory with a `SKILL.md` file:

```
skills/
├── commit-conventions/
│   └── SKILL.md
├── jira-adf/
│   └── SKILL.md
└── ...
```

## How they load

Agents reference skills via `skill://` globs:

```json
{
  "resources": [
    { "type": "skill", "path": "~/.kiro/tuimm/skills/**/SKILL.md" }
  ]
}
```

Skills are loaded on-demand — the agent reads them when the topic comes up, not at startup.
