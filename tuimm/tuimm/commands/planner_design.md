---
name: planner_design
description: "Produce technical design with specialist consultation. Use when: user says 'design [topic]', 'plan [topic]', or after $planner_analyze determines level 3."
---

# Command: $planner_design

Full technical design — consult specialists, produce DESIGN.md in `.plan/{topic}/`.

## Inputs

- **topic**: required. What to design (e.g., "search refactor", "MCP Gateway", ticket ID).
- **analysis**: optional. Output from $planner_analyze if already run.

## Process

### 1. Deep Codebase Analysis

- Read affected code thoroughly (not just grep — understand the architecture)
- Map dependencies, data flow, API contracts
- Identify constraints (tech stack, timeline, existing patterns)
- Search web for prior art if the topic involves external libraries or patterns

### 2. Consult Specialists

Delegate read-only queries to relevant Tier 1 agents:

| Specialist | Query |
|-----------|-------|
| Quality Guardian | "What are the quality constraints and known debt in {affected areas}?" |
| Observability | "What monitoring exists for {affected services}? Any error patterns?" |
| Design System | "What component implications does {topic} have? Figma alignment needed?" |
| Knowledge | "What existing documentation or prior decisions exist for {topic}?" |
| DevEx | "Does {topic} need feature flags, i18n changes, or content model updates?" |

Skip specialists not relevant to the topic.

### 3. Produce DESIGN.md

Create `.plan/{topic}/DESIGN.md` using the planner-design template. Follow it EXACTLY.

### 4. Present to User

Show the full DESIGN.md for review.

**Wait for user approval or feedback before proceeding.**

User can:
- Approve as-is → proceed to decompose
- Request changes → iterate on the design
- Reject → stop
