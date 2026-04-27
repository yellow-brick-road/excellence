
# AI Usage Tracking in Jira

Three dropdown fields on standard issue types (Story, Task, Bug, Debt, Risk). Active since 1 April 2026.

## Purpose

Measure AI usage to understand where adoption improves delivery outcomes — by correlating AI usage trends with delivery KPIs (lead time, throughput, quality). AI usage is NOT a goal in itself.

## Fields

| Field | Set when | Covers |
|-------|----------|--------|
| AI usage during Refinement | DoR reached | Requirement elaboration, story shaping, analysis |
| AI usage during Development | DoD reached | Coding, unit testing, refactoring, code reviews |
| AI usage during Test & Release | Issue done/resolved | Non-dev testing, release prep, deployment |

## Bands

| Band | Value |
|------|-------|
| No AI used | 0% |
| Minimal AI assistance | ~10% |
| Some AI assistance | ~25% |
| Moderate AI assistance | ~50% |
| Mostly AI delivered | ~75% |
| Fully AI delivered | 90-100% |

## Agent Guidelines

When a TUIMM agent solves a ticket:
- **Development**: "Mostly AI delivered (~75%)" or "Fully AI delivered (90-100%)"
- **Refinement**: "Some AI assistance (~25%)" if agent analyzed the ticket and proposed a plan
- **Test & Release**: Do NOT set — handled by QA/release process

When a TUIMM agent addresses MR review comments:
- **Development**: "Mostly AI delivered (~75%)" if not already set

## How to Set

**Manual:** `$jira_set-ai-usage DIS-1234 development fully`

**Automatic:** `$dev_solve` and `$mr_review` set the field as part of their post-MR workflow.

Via Jira subagent: update the issue field with the band string value.

## Safety

- If the field doesn't exist or the update fails, skip silently and inform the user
- NOT on sub-tasks, Epics, or Initiatives (avoids double counting)
- Do NOT use to compare/rank teams or judge performance
