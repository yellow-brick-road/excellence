---
name: tuimm-obs-workflow
description: Observability workflow commands for production error scanning and investigation. Use when checking prod errors, running morning scans, or investigating specific errors.
---

# Observability Workflow

Commands for the tuimm_observability agent: error scanning and investigation.

## Available Commands

- `$obs_dd-scan` — "scan", "morning scan", "check prod errors" — Production error scan with time-aware window. Read the command from [commands/dd-scan.md](commands/dd-scan.md)
- `$obs_dd-investigate` — "investigate [error]" — Deep investigation of a specific error. Read the command from [commands/dd-investigate.md](commands/dd-investigate.md)

## Templates

- [assets/templates/obs-scan-summary.md](assets/templates/obs-scan-summary.md)
- [assets/templates/obs-investigate.md](assets/templates/obs-investigate.md)
