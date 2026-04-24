# What's in this folder

This is the TUIMM package — everything an agent needs to work. After installation, this lives at `~/.kiro/tuimm/`.

For credentials and installation steps, see [SETUP.md](SETUP.md).

---

## steering/

The rules. Every agent reads all 11 steering files before doing anything — they define how agents behave: git conventions, coding standards, communication style, error handling. Non-negotiable.

Think of it as the team's engineering handbook, but machine-readable.

---

## skills/

Self-contained knowledge and workflow packages, following the [agentskills.io](https://agentskills.io) standard. Each skill is a folder with:

```
skill-name/
├── SKILL.md              # Required: metadata + instructions
├── commands/             # Executable workflows (step-by-step recipes)
├── references/           # Additional documentation
└── assets/
    └── templates/        # Output format definitions
```

There are two types of skills:

**Workflow skills** (11) — contain commands and templates for a specific domain. Each agent loads only the skills relevant to its domain. Users trigger commands with `$command-name` or natural language.
- `dev-workflow`, `mr-workflow`, `obs-workflow`, `qg-workflow`, `devex-workflow`, `ds-workflow`, `kn-workflow`, `planner-workflow`
- `jira-workflow`, `weblate-workflow` (shared across multiple agents)
- `get-commands` (meta, available to all agents)

**Knowledge skills** (14) — reference material agents read when they need specific expertise. For example: before creating a Jira ticket, the agent reads `jira-adf` for Atlassian Document Format. Before committing, it reads `commit-conventions` for the format rules.

All skills load on-demand via progressive disclosure — agents see only the name and description at startup, and load the full content only when a task matches.

---

## tools/

Standalone scripts that agents run via shell. Not AI — just Python and Bash doing mechanical work.

The main ones:
- **guidelines-generator** — extracts coding conventions from real code (supports Nuxt, Java, Python, Go)
- **autobuild** — task engine that executes multi-step plans
- **gitlab-list-mrs.py** — queries GitLab for MRs across repos
- **bg** and **logd** — background execution and structured logging for long-running tasks

---

## prompts/

Empty. Reserved for future multi-agent workflows. Not used yet.
