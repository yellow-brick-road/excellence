---
name: tuimm-guidelines-generator
description: |
  guidelines-generator — AI-powered coding convention extractor.
  Use when: generating coding guidelines from a codebase, running extraction pipelines,
  checking guideline generation progress, or understanding how the tool works.
---

# Guidelines Generator

Extracts coding conventions from real codebases via AI. Scans committed files, asks an agent to propose categories, then extracts patterns per category through a 4-phase pipeline (extract → review → split → refine).

## Script

`scripts/guidelines-generator.py` — the main extraction engine.

## Available Commands

| Command | Trigger | Description |
|---------|---------|-------------|
| `$qg_generate-guidelines` | "generate guidelines", "extract conventions" | Run the full guidelines extraction pipeline |

When the user invokes a command, read the corresponding file from `commands/` and follow the steps.

## Usage

```bash
# Scan — see what's in the repo
cd ~/work/my-project
python3 ~/.kiro/skills/tuimm-guidelines-generator/scripts/guidelines-generator.py --scan

# Run full pipeline in background
python3 ~/.kiro/skills/tuimm-guidelines-generator/scripts/guidelines-generator.py --phase all --bg -y

# Check progress
python3 ~/.kiro/skills/tuimm-guidelines-generator/scripts/guidelines-generator.py --report

# Stop if needed
python3 ~/.kiro/skills/tuimm-guidelines-generator/scripts/guidelines-generator.py --stop
```

Supports Nuxt/Vue/TS (default), Java, Python, Go via `--extensions` flag.
Output goes to `docs/guidelines/` in the project root.

## Templates

- `qg-generate-guidelines.md` — output format for the guidelines generation report
- `guidelines-generator/extract.md` — extraction prompt template used by the Python script
