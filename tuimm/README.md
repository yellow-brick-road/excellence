# What's in this folder

This is the TUIMM package — everything an agent needs to work. After installation, contents go to `~/.kiro/` (global), with `tuimm-` and `tuimm/` prefixes to avoid collisions with other packages.

For credentials and installation steps, see [SETUP.md](SETUP.md).

---

## steering/

The rules. Every agent reads all 11 `*.md` steering files before doing anything — they define how agents behave: git conventions, coding standards, communication style, error handling. Non-negotiable.

Installed to: `~/.kiro/steering/tuimm/*.md`

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

26 skills total: 12 workflow skills (with commands and templates) + 14 knowledge skills (reference material only). Installed with `tuimm-` prefix to avoid collisions.

Installed to: `~/.kiro/skills/tuimm-*/`

---

## tuimm/

Lightweight directory used as the knowledgeBase index target. Contains only a README explaining the TUIMM package structure. Agents index this directory for semantic search.

Installed to: `~/.kiro/tuimm/`

---

## prompts/

Empty. Reserved for future multi-agent workflows.
