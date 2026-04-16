---
name: ds-component-check
description: "Component check report for $ds_component-check. Use when: presenting Figma vs code comparison."
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Component Check — {component_name}
   Figma: {figma_url}
   Code: {file_path}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Props: {matched}/{total} ✅ | {missing} missing | {extra} extra
Visual: {matched}/{total} ✅ | {drift} drift
Naming: ✅/❌
Accessibility: {issues} issues
Quality: {rating}

📐 Props comparison:
| Figma Prop | Code Prop | Status |
|------------|-----------|--------|

🎨 Visual specs:
| Property | Figma | Code | Status |
|----------|-------|------|--------|

💡 Recommended fixes:
1. {fix}

RULES: This is the COMPLETE output. Omit empty sections. Do NOT add commentary or follow-up questions.
