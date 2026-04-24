---
verify: "test -s {OUTPUT_PATH}"
creates: ["{OUTPUT_PATH}"]
timeout: 120
type: extract
---

# Extract guidelines from {SOURCE_PATH}

Read the file `{SOURCE_PATH}`.
This is a {CATEGORY} file in a {FRAMEWORK} project.

Extract ONLY generalizable, reusable conventions for writing new {CATEGORY}.
Focus on: structure, API choices, naming, styling, typing, patterns.

Format as short actionable rules (style-guide bullets).
Good: '- Use `<script setup lang="ts">` for all components'
Bad: '- This file imports useRoute from vue-router'

Output ONLY bullet points (- rule), one per line.
No commentary, no annotations, no reasoning.
If nothing useful, output EXACTLY: NONE

Write output to `{OUTPUT_PATH}`.
