# What's in this folder

This is the TUIMM package — everything an agent needs to work. After installation, this lives at `~/.kiro/tuimm/`.

For credentials and installation steps, see [SETUP.md](SETUP.md).

---

## steering/

The rules. Every agent reads all 11 steering files before doing anything — they define how agents behave: git conventions, coding standards, communication style, error handling. Non-negotiable.

Think of it as the team's engineering handbook, but machine-readable.

---

## commands/

The workflows. Each command is a step-by-step recipe for a specific task: "how to solve a Jira ticket", "how to review an MR", "how to scan production errors."

**Why commands instead of prompts?** Kiro CLI has prompts (`@name`) — they're global, every agent sees all of them. If you put 36 workflows as prompts, every agent loads all 36 at startup. The list becomes noise and the agent can't tell which ones are relevant.

Commands solve this with scoping. Each agent only loads its own commands via prefix:
- Dev loads `dev_*` + `jira_*` + `weblate_*` → 10 commands
- MR loads `mr_*` + `jira_*` + `weblate_*` → 12 commands
- Quality Guardian loads `qg_*` + `jira_*` → 10 commands

Each agent has a short, focused menu. It knows exactly what it can do. Users trigger them with `$command-name` or natural language.

Commands also load on-demand (as skills), not at startup — they don't bloat the agent's context until they're actually needed.

---

## skills/

Reference knowledge. Not executable — agents read them when they need specific expertise.

For example: before creating a Jira ticket, the agent reads the `jira-adf` skill to understand Atlassian Document Format. Before committing code, it reads `commit-conventions` for the format rules. Before reviewing code, it reads `code-review-checklist` for what to look for.

14 skills covering: commit format, GitLab conventions, Jira format, Weblate workflow, code review checklist, MCP tool reference, known error patterns, and more.

---

## templates/

Output formats. Commands say "present results using the X template" — the template defines the exact structure so every output looks consistent.

Every MR review has the same sections. Every quality check has the same format. Every scan summary follows the same pattern. 37 templates, one per command output.

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
