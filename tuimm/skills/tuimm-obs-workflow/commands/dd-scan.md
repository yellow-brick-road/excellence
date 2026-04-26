---
name: obs_dd-scan
description: "Production error scan. Use when: user says 'scan', 'morning scan', or 'check prod errors'."
---

# Command: $obs_dd-scan

Production error scan. Deep analysis, not just counts.

## Time Window

- **Monday**: Friday 18:00 to now (full weekend)
- **Other days**: Last 24h

## Step 0: Required Context (ask before anything)

Ask the user these questions. Do NOT proceed until all are answered:

1. **Service name** — exact Datadog service name (e.g. `b2c-tuimusement-frontend`). If unsure, search available services via tuimm_subagent_datadog first.
2. **Repo** — GitLab repo path (e.g. `distribution/b2c-tuimusement-frontend`). Needed for code investigation later.
3. **Deployed version** — current commit hash or tag in prod. Check Datadog logs `@version` tag if user doesn't know. Also ask about recent deploys in the scan window — useful to correlate regressions.

Once a shared service registry exists, these can be auto-resolved. Until then, ask every time.

## Process

### 1. Load Previous Scan

```bash
python3 ~/.kiro/skills/tuimm-logd-reference/scripts/extensions/obs_scan.py load-previous --service {service}
```

If `{"found": true}` — extract previous patterns and counts for comparison in Step 6.
If `{"found": false}` — skip comparison, all patterns will be 🆕 NEW.

If the script fails (logd not installed, DB missing), skip silently and treat as no previous scan.

### 2. Aggregate Errors — Two Passes

Run TWO aggregate queries via tuimm_subagent_datadog:

**Pass 1 — Real users:**
```
service:{service} status:error env:prod -@http.useragent_details.device.category:Bot -@http.useragent:HeadlessChrome*
```

**Pass 2 — Bots only:**
```
service:{service} status:error env:prod (@http.useragent_details.device.category:Bot OR @http.useragent:HeadlessChrome*)
```

For each pass, use `aggregate-logs` with groupBy `@error.message`.

**API rules (critical):**
- ✅ groupBy `@error.message` — works
- ✅ groupBy `@error.kind` — works
- ❌ Do NOT add `sort` to groupBy — API fails
- ❌ Do NOT add `limit` to groupBy — API fails (default is 10, fixed)
- ❌ `message` is NOT a valid facet for groupBy

### 3. Complement with @error.kind

Run a second aggregation per pass with groupBy `@error.kind`. Since groupBy caps at 10 results, this catches error types not in the top 10 messages.

### 4. Time Buckets (weekends only)

If scan window > 24h (Monday scans), split into 6h sub-windows and run aggregate-logs per bucket. This shows when spikes started and whether they're recovering.

For normal days (≤24h window), skip — single window is enough.

### 5. Detail per Pattern

For each pattern from the top results, run `search_logs` filtered by `@error.message:"{pattern}"` to get one representative log with:
- Full stack trace (`@error.stack`)
- Affected URL (`@http.url` or `@view.url`)
- User agent
- Custom context (`@error.data.context`)

### 6. Classify

**Compare with previous scan + tuimm-known-error-patterns skill:**

| Status | Condition |
|--------|-----------|
| 🆕 NEW | Not in previous scan |
| 🔄 RECURRING | Was in previous scan, still present |
| 📈 SPIKE | Was in previous scan, count increased >2x |
| ✅ RESOLVED | Was in previous scan, gone now |

Check the tuimm-known-error-patterns skill for baseline severity and context. Override severity if the pattern is known and documented.

**Severity:**

| Severity | Criteria |
|----------|----------|
| 🔴 CRITICAL | >50 occurrences OR affects checkout/payment |
| 🟠 HIGH | 20-50 occurrences OR new error with stack trace |
| 🟡 MEDIUM | 5-19 occurrences |
| ⚪ LOW | <5 occurrences |

### 7. Save to logd

```bash
python3 ~/.kiro/skills/tuimm-logd-reference/scripts/extensions/obs_scan.py save '{JSON}'
```

Build the JSON with service, repo, version, window, all patterns, and summary. See the script for the expected schema.

If save fails, warn the user but don't fail the scan.

### 8. Output (LAST STEP — nothing after this)

Present results using the obs-scan-summary template. Follow it EXACTLY — no extra sections, no extra columns, no markdown headers. Do NOT add follow-up questions or commentary after the template.

## Fallback Chain

When a query fails, don't lose data silently:

1. `aggregate-logs` with groupBy → if fails:
2. `aggregate-logs` without groupBy (total count only) → if fails:
3. `search_logs` paginated (up to 100 logs) + manual counting → if fails:
4. Report which queries failed and why in the output

Always note in the output if a fallback was used.
