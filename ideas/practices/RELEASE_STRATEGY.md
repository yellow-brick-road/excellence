# Release Strategy

> Status: Idea
> Author: Javier Fernández
> Created: 2026-03-05

## The Pain

Nobody likes semantic-release. It's the tool everyone adopted because "automated versioning" sounded good, but the reality is:

- **Black box** — commits go in, versions come out, nobody understands why a patch became a minor or why nothing bumped at all
- **Commit-prefix roulette** — miss a `feat:` and your feature doesn't bump. Typo in the prefix? Silent failure. The version depends on humans writing perfect commit messages, which defeats the purpose of automation
- **Config hell** — plugins, branches, channels, pre-releases, release candidates. The `.releaserc` becomes its own maintenance burden
- **Monorepo pain** — semantic-release + Lerna/workspaces = fragile coordination. Independent versioning across packages is a constant source of broken releases
- **Mediocre changelogs** — a dump of commit messages is not a changelog. "fix: stuff" tells nobody anything. The output is technically correct and practically useless
- **Zero judgment** — a machine decides patch/minor/major based on text prefixes. It can't know that your "fix" actually changed the public API, or that three "feat" commits are really one feature
- **CI coupling** — deeply embedded in pipeline config, hard to debug, harder to override when it gets it wrong

The current state at TUI: Lerna 9.x for publishing in `b2c-nuxt-libraries`, semantic-release conventions assumed but inconsistently followed. The friction is real and it compounds across repos.

## The Principle

> Releases should be intentional, informed, and progressively autonomous.

A release is a decision, not a side effect of commit messages. The tooling should help humans make better release decisions faster — and eventually make those decisions autonomously when confidence is high enough.

## Options

### Option A — Status Quo (semantic-release)

Keep semantic-release, invest in better config and commit discipline.

- ✅ Already in place
- ✅ Industry standard, well-documented
- ❌ Doesn't fix the fundamental problems
- ❌ Requires perfect commit hygiene org-wide (unrealistic)
- ❌ Changelogs remain useless

**Verdict:** Polishing a tool nobody trusts doesn't build trust.

### Option B — Agent-Driven Releases (recommended)

Replace semantic-release with an AI agent that understands code, not just commit prefixes.

Three progressive levels:

#### Level 1 — Manual with Agent Assist (`$release`)

A command on the Quality Guardian agent. Developer triggers it explicitly.

1. Analyze actual code diff since last tag (not commits — AST-level changes, exports, API surface)
2. Cross-reference with Jira tickets linked to merged MRs
3. Propose version bump with reasoning ("minor: new composable `useBooking` exported, 2 new props on `SearchBar`")
4. Generate meaningful changelog grouped by impact (breaking, features, fixes, internal)
5. Human reviews, adjusts if needed, approves
6. Agent executes: version bump in `package.json`, changelog update, git tag, npm publish via `subagent_npm` (existing TARS subagent — bash wrapper, no dedicated spec), tag via `subagent_gitlab`

**Why this works:**
- The agent reads code, not commit messages. It knows what actually changed
- Changelog has real context: Jira tickets, MR links, actual impact description
- Human stays in the loop for the decision that matters: "is this ready to release?"
- No commit convention dependency for versioning (conventions still useful for history, just not for automation)

#### Level 2 — Semi-Autonomous (Bot Service)

Event-driven via the Autonomous Bot Service:

1. Merge to `main` → webhook triggers bot
2. Bot analyzes accumulated changes since last release
3. Creates a "Release Proposal" MR with:
   - Proposed version bump + reasoning
   - Generated changelog
   - Updated `package.json`
4. Human approves MR → pipeline publishes
5. Bot notifies relevant channels

**Like Renovate, but for your own releases.** The bot proposes, the human disposes.

#### Level 3 — Full Autonomous

Bot decides, publishes, notifies. Human intervention only for:
- Major version bumps (breaking changes)
- First release of a new package
- Rollback scenarios

Post-publish validation: if smoke tests fail after publish, auto-deprecate the version and alert.

### Option C — Hybrid

Keep semantic-release for simple repos (single package, clear commit discipline), use agent-driven for monorepos and complex packages.

- ✅ Pragmatic, no big-bang migration
- ❌ Two systems to maintain
- ❌ Inconsistent experience across repos

## Recommendation

**Option B, starting at Level 1.** The `$release` command is low-cost to build (it's a command using existing subagents), immediately useful, and sets the foundation for Level 2 when the Bot Service ships.

Migration path:
1. Build `$release` command on Quality Guardian
2. Pilot on `b2c-nuxt-libraries` (highest pain, most packages)
3. If it works, disable semantic-release, use `$release` as the standard
4. When Bot Service ships (Phase 3), upgrade to Level 2

## What the Agent Knows That semantic-release Doesn't

| Signal | semantic-release | Agent |
|--------|-----------------|-------|
| Commit message prefix | ✅ | ✅ (but doesn't depend on it) |
| Actual code diff | ❌ | ✅ AST-level analysis |
| Exported API changes | ❌ | ✅ detects new/removed/changed exports |
| Breaking change detection | Only if `BREAKING CHANGE:` in commit | ✅ analyzes type signatures, removed props, changed interfaces |
| Jira ticket context | ❌ | ✅ via `subagent_jira` |
| MR descriptions | ❌ | ✅ via `subagent_gitlab` |
| Cross-package impact | Fragile (Lerna heuristics) | ✅ follows dependency graph |
| Changelog quality | Commit dump | Contextual, grouped by impact |

## Implementation

### Phase 1 — Build the Command

- [ ] Define `COMMAND_QG_RELEASE.md` spec (see `ideas/ai/COMMAND_QG_RELEASE.md`)
- [ ] Implement diff analysis logic (compare last tag to HEAD)
- [ ] Implement version proposal heuristics
- [ ] Implement changelog generation template
- [ ] Wire up `subagent_gitlab` (tags, MR info) + `subagent_npm` (publish — existing TARS subagent, bash wrapper)
- [ ] Wire up `subagent_jira` (ticket context for changelog)

### Phase 2 — Pilot

- [ ] Test on `b2c-nuxt-libraries`
- [ ] Compare agent-proposed versions vs what semantic-release would have done
- [ ] Gather developer feedback
- [ ] Iterate on changelog format

### Phase 3 — Roll Out

- [ ] Disable semantic-release on piloted repos
- [ ] Document the `$release` workflow
- [ ] Extend to other repos
- [ ] When Bot Service ships, add webhook trigger for Level 2

## Connection to Excellence

- **Pipeline Optimization** — release is the last mile of the pipeline. Faster, smarter releases = faster delivery
- **Repo Strategy** — monorepo releases are the hardest case. Agent-driven handles cross-package dependencies better than Lerna heuristics. The shared library's auto-propagation system (see REPO_STRATEGY.md) is the consumer-side counterpart: `$release` publishes with rich context, the bot propagates to consumers with auto-fix
- **Ticket Standardization** — structured tickets feed better changelogs. The release agent benefits from good ticket hygiene
- **Autonomous Bot Service** — Level 2/3 are direct consumers of the bot infrastructure

### KPI

- Time from "ready to release" to "published on npm" (target: < 5 min with Level 1)
- Changelog usefulness (qualitative — do developers actually read them?)
- Version accuracy (does the bump match the actual change scope?)
- Failed releases / rollbacks per quarter

## Open Questions

- [ ] Who currently triggers releases? Is it manual or CI-driven?
- [ ] Are there repos where semantic-release works fine and shouldn't be touched?
- [ ] What's the appetite for removing semantic-release entirely vs keeping it as fallback?
- [ ] Do we need npm provenance / signed packages?
- [ ] How do we handle pre-releases and release candidates in the agent model?
