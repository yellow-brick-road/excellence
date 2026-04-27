---
name: tuimm-jira-adf
description: |
  Atlassian Document Format (ADF) reference for Jira description and comment fields.
  Use when: writing Jira ticket descriptions, adding comments, or building ADF payloads for the Atlassian API.
  Contains: minimum valid structure, block nodes, inline marks, common patterns, formatting rules.
---

# Atlassian Document Format (ADF)

Jira `description` and `comment` fields require ADF, NOT plain text.

## Minimum Valid Structure

```json
{
  "type": "doc",
  "version": 1,
  "content": [...]
}
```

## Block Nodes

### Paragraph

```json
{ "type": "paragraph", "content": [{ "type": "text", "text": "Text here" }] }
```

### Heading (levels 1-6)

```json
{ "type": "heading", "attrs": { "level": 2 }, "content": [{ "type": "text", "text": "Title" }] }
```

### Bullet List

```json
{
  "type": "bulletList",
  "content": [
    { "type": "listItem", "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Item 1" }] }
    ]},
    { "type": "listItem", "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Item 2" }] }
    ]}
  ]
}
```

### Ordered List

Same as bulletList but `"type": "orderedList"`.

### Code Block

```json
{ "type": "codeBlock", "attrs": { "language": "typescript" }, "content": [{ "type": "text", "text": "const x = 1;" }] }
```

### Rule (horizontal line)

```json
{ "type": "rule" }
```

## Inline Marks

Apply to text nodes via `marks` array:

```json
{ "type": "text", "text": "bold text", "marks": [{ "type": "strong" }] }
```

| Mark | Type |
|------|------|
| Bold | `{ "type": "strong" }` |
| Italic | `{ "type": "em" }` |
| Code | `{ "type": "code" }` |
| Link | `{ "type": "link", "attrs": { "href": "https://..." } }` |

## Common Patterns

### Heading + Bullets (for ticket sections)

```json
[
  { "type": "heading", "attrs": { "level": 2 }, "content": [{ "type": "text", "text": "Acceptance Criteria" }] },
  { "type": "bulletList", "content": [
    { "type": "listItem", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Criterion 1" }] }] },
    { "type": "listItem", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Criterion 2" }] }] }
  ]}
]
```

## Rules

- Every text must be inside a paragraph or heading — never bare text in doc.content
- listItem must contain paragraph (not bare text)
- Empty content arrays are invalid — omit the field or provide content
