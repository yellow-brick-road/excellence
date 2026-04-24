---
name: mr-workflow
description: Merge request workflow commands for review, feedback, approval, rebasing, and listing MRs. Use when reviewing code, addressing comments, or managing MR lifecycle.
---

# MR Workflow

Commands for the tuimm_mr agent: MR review, comment handling, approval, rebase, and listing.

## Available Commands

- `$mr_review` — "review [MR-ID]" — Full MR review with structured feedback. Read the command from [commands/review.md](commands/review.md)
- `$mr_comments` — "comments [MR-ID]" — Fetch and address review comments. Read the command from [commands/comments.md](commands/comments.md)
- `$mr_approve` — "approve [MR-ID]" — Approve a merge request. Read the command from [commands/approve.md](commands/approve.md)
- `$mr_rebase` — "rebase [MR-ID]" — Rebase MR via GitLab API. Read the command from [commands/rebase.md](commands/rebase.md)
- `$mr_list` — "list" — List open MRs across tracked repos. Read the command from [commands/list.md](commands/list.md)

## Templates

- [assets/templates/mr-review-summary.md](assets/templates/mr-review-summary.md)
- [assets/templates/mr-comments-summary.md](assets/templates/mr-comments-summary.md)
- [assets/templates/mr-comment-item.md](assets/templates/mr-comment-item.md)
- [assets/templates/mr-approve.md](assets/templates/mr-approve.md)
- [assets/templates/mr-rebase.md](assets/templates/mr-rebase.md)
- [assets/templates/mr-list-summary.md](assets/templates/mr-list-summary.md)
