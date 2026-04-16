# Command: $onboarding

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `kn_onboarding`
> Description: Generate personalized onboarding guide for a new team member. Maps repos, tools, documentation, suggests first tasks.
> Agent: Knowledge

## Trigger

`$onboarding [team]` or "onboarding guide", "new joiner guide"

## Workflow

1. `subagent_confluence` → find existing onboarding docs for the team
2. `subagent_jira` → get team's active project and board
3. `subagent_gitlab` → list team's repos with descriptions
4. `subagent_contentful` → list relevant content models (if applicable)
5. Compile: repos, tools, access needed, key documentation
6. Suggest first tasks based on team's current sprint
7. `subagent_confluence` → create personalized onboarding page

## Output

Confluence page with:
- Team overview and contacts
- Repos and their purpose
- Tools and access needed (with links)
- Key documentation to read
- Development setup guide
- Suggested first tasks
- Team conventions and standards

## Phase

Phase 2 (requires Confluence subagent)
