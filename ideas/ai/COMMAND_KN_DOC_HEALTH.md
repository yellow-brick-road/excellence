# Command: $doc-health

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


> Command name: `kn_doc_health`
> Description: Documentation health audit across Confluence spaces. Detect stale pages, orphans, broken links, calculate freshness scores per team.
> Agent: Knowledge

## Trigger

`$doc-health` or "doc health", "documentation health", "docs audit"

## Workflow

1. `subagent_confluence` → list pages across configured spaces
2. `subagent_confluence` → detect stale pages (not updated in X months)
3. `subagent_confluence` → find orphan pages (no incoming links)
4. `subagent_confluence` → check for broken links
5. `subagent_confluence` → get page view stats (most/least viewed)
6. Calculate freshness score per space/team
7. Check minimum docs per project (README, architecture, deployment)
8. Generate health report with action items

## Output

- Documentation coverage per team (% of projects with docs)
- Freshness score per space (average age of last update)
- Stale pages (list with last update date)
- Orphan pages (no links pointing to them)
- Broken links
- Missing minimum docs per project
- Recommended actions

## Phase

Phase 2 (requires Confluence subagent)
