---
name: tuimm-dev-workflow
description: Development workflow commands for ticket-to-MR lifecycle. Use when implementing features, solving tickets, or continuing interrupted work.
---

# Dev Workflow

Commands for the tuimm_dev agent's core workflow: reading requirements, implementing changes, and creating merge requests.

## Available Commands

- `$dev_solve` — "solve DIS-XXXX" — Full ticket-to-MR workflow. Read the command from [commands/solve.md](commands/solve.md)
- `$dev_implement` — "implement [description]" — Implementation only (no ticket read). Read the command from [commands/implement.md](commands/implement.md)
- `$dev_continue` — "continue" — Resume interrupted work. Read the command from [commands/continue.md](commands/continue.md)

## Templates

- [assets/templates/dev-solve.md](assets/templates/dev-solve.md) — Output format for solve command
- [assets/templates/dev-continue.md](assets/templates/dev-continue.md) — Output format for continue command
