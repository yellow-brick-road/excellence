# Idea: Datadog Subagent

> ⚠️ **Design document.** The implementation in `.kiro/` may differ. For current state, see the actual steering files and agent JSONs.


## Title

Tool subagent for Datadog monitoring operations via TUI MCP Gateway.

## Context

API wrapper for Datadog. Handles log search, APM traces, metrics, and RUM data. Connected through the centralized MCP Gateway. Primarily used by the Observability agent.

Based on existing Datadog MCP (`datadog-mcp-server`) with `datadoghq.eu` site.

## MCP Connection

Via TUI MCP Gateway → Datadog API (`datadoghq.eu`)

## Capabilities

### Logs
- Search logs by query (service, status, environment, message, tags)
- Get log details (full message, attributes, tags)
- Filter by time range
- Exclude bots (`-@http.useragent_details.device.category:Bot`)
- Paginate through large result sets

### APM (Traces)
- Search traces by service, operation, status
- Get trace details (spans, duration, errors)
- Get service dependencies (service map)
- Get latency percentiles per endpoint

### Metrics
- Get metric data (timeseries)
- List available metrics per service
- Get metric metadata
- Query custom metrics

### RUM (Real User Monitoring)
- Get page load performance data
- Get Core Web Vitals (LCP, FID, CLS)
- Get user session data
- Get error data from real users
- Filter by country, device, browser

### Services
- List monitored services
- Get service overview (error rate, latency, throughput)
- Get service dependencies

### Intelligence (light)
- Normalize error messages (strip dynamic values like IDs, URLs, timestamps)
- Group logs by error pattern
- Calculate error frequency and trends
- Detect anomalies in error rates

## Used By

- Observability Agent → error investigation, morning scan, performance monitoring
- Quality Guardian → correlate code quality with production errors
- Excellence Default → ad-hoc monitoring queries
