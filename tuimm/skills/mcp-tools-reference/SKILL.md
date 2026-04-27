---
name: mcp-tools-reference
description: |
  MCP tool reference for TUIMM agents — read vs write classification per server.
  Use when: configuring allowedTools for agents, restricting to read-only access,
  or checking what operations each MCP server supports.
  Contains: all tools per MCP server, classified as READ or WRITE.
---

# MCP Tools Reference

Tool classification for all TUIMM MCP servers. Use this to configure `allowedTools` per agent.

## @atlassian (Jira + Confluence)

### Jira

| Tool | Type | Description |
|------|------|-------------|
| `getJiraIssue` | READ | Get issue details |
| `searchJiraIssuesUsingJql` | READ | Search issues with JQL |
| `getTransitionsForJiraIssue` | READ | Get available transitions |
| `getJiraIssueRemoteIssueLinks` | READ | Get remote issue links |
| `getVisibleJiraProjects` | READ | List visible projects |
| `getJiraProjectIssueTypesMetadata` | READ | Get project issue types |
| `getJiraIssueTypeMetaWithFields` | READ | Get issue type field metadata |
| `lookupJiraAccountId` | READ | Look up user account ID |
| `createJiraIssue` | WRITE | Create new issue |
| `editJiraIssue` | WRITE | Update issue fields |
| `transitionJiraIssue` | WRITE | Change issue status |
| `addCommentToJiraIssue` | WRITE | Add comment to issue |
| `addWorklogToJiraIssue` | WRITE | Add worklog entry |

### Confluence

| Tool | Type | Description |
|------|------|-------------|
| `getConfluencePage` | READ | Get page content by ID |
| `getConfluenceSpaces` | READ | List available spaces |
| `getPagesInConfluenceSpace` | READ | List pages in a space |
| `getConfluencePageDescendants` | READ | Get child/descendant pages |
| `searchConfluenceUsingCql` | READ | Search with CQL |
| `getConfluencePageFooterComments` | READ | Get footer comments |
| `getConfluencePageInlineComments` | READ | Get inline comments |
| `getConfluenceCommentChildren` | READ | Get comment replies |
| `createConfluencePage` | WRITE | Create new page |
| `updateConfluencePage` | WRITE | Update existing page |
| `createConfluenceFooterComment` | WRITE | Add footer comment |
| `createConfluenceInlineComment` | WRITE | Add inline comment |

### General

| Tool | Type | Description |
|------|------|-------------|
| `getAccessibleAtlassianResources` | READ | List accessible resources |
| `atlassianUserInfo` | READ | Get current user info |
| `fetch` | READ | Fetch URL content |

## @gitlab

| Tool | Type | Description |
|------|------|-------------|
| `list_projects` | READ | List accessible projects |
| `get_project` | READ | Get project details |
| `list_merge_requests` | READ | List MRs (filter by state, scope) |
| `get_merge_request` | READ | Get MR details |
| `get_merge_request_diffs` | READ | Get MR diff |
| `list_merge_request_discussions` | READ | Get MR threads |
| `list_pipelines` | READ | List pipelines |
| `get_pipeline` | READ | Get pipeline details |
| `list_branches` | READ | List branches |
| `create_merge_request` | WRITE | Create new MR |
| `update_merge_request` | WRITE | Update MR |
| `create_merge_request_note` | WRITE | Add comment |
| `resolve_discussion` | WRITE | Resolve thread |
| `create_branch` | WRITE | Create branch |

## @sonarqube (all READ)

| Tool | Type | Description |
|------|------|-------------|
| `search_issues` | READ | Search issues by project, severity, status |
| `get_issue` | READ | Get issue details |
| `get_quality_gate` | READ | Get quality gate status |
| `get_measures` | READ | Get metrics (coverage, bugs, vulnerabilities) |
| `get_rule` | READ | Get rule details |
| `list_projects` | READ | List projects |

## @datadog (all READ)

| Tool | Type | Description |
|------|------|-------------|
| `search_logs` | READ | Search logs with query |
| `get_log` | READ | Get log details |
| `list_services` | READ | List monitored services |
| `get_metrics` | READ | Get metric data |

## @figma (all READ)

| Tool | Type | Description |
|------|------|-------------|
| `get_figma_data` | READ | Get design context from Figma URL |

## @contentful

| Tool | Type | Description |
|------|------|-------------|
| `list_content_types` | READ | List content types |
| `get_content_type` | READ | Get content type details |
| `list_entries` | READ | List entries |
| `get_entry` | READ | Get entry details |
| `list_assets` | READ | List assets |
| `get_asset` | READ | Get asset details |
| `list_locales` | READ | List locales |
| `create_entry` | WRITE | Create entry |
| `update_entry` | WRITE | Update entry |
| `publish_entry` | WRITE | Publish entry |
| `delete_entry` | WRITE | Delete entry |

## @configcat

| Tool | Type | Description |
|------|------|-------------|
| `list_flags` | READ | List feature flags |
| `get_flag` | READ | Get flag details |
| `list_environments` | READ | List environments |
| `get_flag_value` | READ | Get flag value per environment |
| `list_segments` | READ | List segments |
| `update_flag` | WRITE | Update flag settings |
| `create_flag` | WRITE | Create flag |

## Quick Copy — Read-Only allowedTools

For agents that should only read:

```json
"allowedTools": [
  "@sonarqube", "@datadog", "@figma",
  "@atlassian/getJiraIssue",
  "@atlassian/searchJiraIssuesUsingJql",
  "@atlassian/getTransitionsForJiraIssue",
  "@atlassian/getJiraIssueRemoteIssueLinks",
  "@atlassian/getVisibleJiraProjects",
  "@atlassian/getJiraProjectIssueTypesMetadata",
  "@atlassian/getJiraIssueTypeMetaWithFields",
  "@atlassian/lookupJiraAccountId",
  "@atlassian/getConfluencePage",
  "@atlassian/getConfluenceSpaces",
  "@atlassian/getPagesInConfluenceSpace",
  "@atlassian/getConfluencePageDescendants",
  "@atlassian/searchConfluenceUsingCql",
  "@atlassian/getConfluencePageFooterComments",
  "@atlassian/getConfluencePageInlineComments",
  "@atlassian/getConfluenceCommentChildren",
  "@atlassian/getAccessibleAtlassianResources",
  "@atlassian/atlassianUserInfo",
  "@gitlab/list_projects",
  "@gitlab/get_project",
  "@gitlab/list_merge_requests",
  "@gitlab/get_merge_request",
  "@gitlab/get_merge_request_diffs",
  "@gitlab/list_merge_request_discussions",
  "@gitlab/list_pipelines",
  "@gitlab/get_pipeline",
  "@gitlab/list_branches"
]
```
