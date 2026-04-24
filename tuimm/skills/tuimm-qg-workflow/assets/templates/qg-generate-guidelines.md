---
name: qg-generate-guidelines
description: "Output format for $qg_generate-guidelines. Use when: presenting guidelines generation instructions."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Generate Guidelines — {project_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project: {path}
Tool: `~/.kiro/tools/guidelines-generator/guidelines-generator.py`

Run:
```bash
python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py {source_dir}
```

Output: `{source_dir}/docs/guidelines/`

Check progress: `python3 ~/.kiro/tools/guidelines-generator/guidelines-generator.py {source_dir} --report`

RULES: This is the COMPLETE output. Do NOT add commentary or follow-up questions.
