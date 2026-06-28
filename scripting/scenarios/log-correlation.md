# Scenario: Cross-Service Log Correlation

## Problem Statement (as interviewer would say it)

> "A payment failed. Auth service logged success, ledger service logged success, notification service logged nothing. How do you debug this across three services?"

---

## Clarifying Questions to Ask

- Are logs structured (JSON) or plain text? Structured logs are required for programmatic trace correlation.
- Are logs on disk, or already in a log aggregation system (Loki, CloudWatch, Elasticsearch)?
- Do all services emit trace IDs on every log line — including error paths?

---

## Core Concept

**Trace IDs** — every log line across every service for the same request shares one ID. Like a ticket number: you pull all records with that number to reconstruct the timeline.

Without a trace ID on error paths, failures become invisible to correlation. An exception handler that writes plain text loses the ID — that log line exists, but the correlation script can't find it.

---

## Worked Solution

```python
#!/usr/bin/env python3
"""Reconstruct request timeline from structured logs using trace ID."""
import json, os, sys

SERVICES = ["auth", "ledger", "notification"]
LOG_DIR = "./logs"

def load_logs():
    all_lines = []
    for svc in SERVICES:
        path = os.path.join(LOG_DIR, f"{svc}.log")
        if not os.path.exists(path):
            print(f"WARNING: no log file for {svc}", file=sys.stderr)
            continue
        with open(path) as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                    parsed["_source"] = svc      # tag with service name for display
                    all_lines.append(parsed)
                except json.JSONDecodeError:
                    # Plain-text line = structured logging gap — flag it
                    # This is where invisible failures hide
                    print(f"WARNING: {svc}.log line {i} not JSON (won't appear in trace):")
                    print(f"  {line[:120]}")
    return all_lines

def correlate(trace_id, all_lines):
    matched = [l for l in all_lines if l.get("trace_id") == trace_id]
    return sorted(matched, key=lambda x: x.get("timestamp", ""))

def main(trace_id):
    all_lines = load_logs()
    matched = correlate(trace_id, all_lines)

    if not matched:
        print(f"No structured log lines found for trace_id={trace_id}")
        return

    seen_services = {l["_source"] for l in matched}
    missing = [s for s in SERVICES if s not in seen_services]

    print(f"\nTimeline — {len(matched)} events across {len(seen_services)} service(s):\n")
    for l in matched:
        ts = l.get("timestamp", "?")
        svc = l.get("_source", "?").upper()
        event = l.get("event", "?")
        level = l.get("level", "INFO")
        print(f"  [{ts}] [{svc}] [{level}] {event}")

    if missing:
        print(f"\nMISSING TELEMETRY: {missing}")
        print("Check raw log files for plain-text error lines around the same timestamp.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python correlate.py <trace_id>")
        sys.exit(1)
    main(sys.argv[1])
```

---

## The "Invisible Failure" Pattern to Explain

> Notification logged `email_send_attempt` (with trace_id) then hit a timeout. The error handler wrote plain text — no trace_id. Timeline shows the attempt, then `payment_complete`. No gap is visible. The failure is in the log file, but invisible to correlation.
>
> Fix: error handlers must emit structured JSON with the same trace_id.

This is the pattern interviewers want to hear: you understand that **absence in the timeline is not absence in the logs** — it's evidence that the trace ID was dropped somewhere.

---

## Key Insight to Say in the Interview

> "A missing service in the timeline isn't just absence — it's evidence. Either the request never reached it, or an error path swallowed the trace ID and logged plain text. The error exists in the log file; the correlation script just can't find it."

---

## Follow-Up Q&A

**"How does this work in Kubernetes?"**
`kubectl logs <pod>` for the current container, `--previous` for the last restart. Anything older requires a log aggregation layer: Loki, CloudWatch Logs, or Elasticsearch/OpenSearch.

**"What's OpenTelemetry?"**
A vendor-neutral standard for propagating trace IDs across services automatically — no manual passing of headers or IDs required. It instruments your code and injects trace context into outbound calls.

**"What if services use different timestamp formats?"**
Normalize to ISO 8601 on ingest. If timestamps aren't reliable, sort by a monotonic sequence ID if available, or by trace span order.

**"What if logs are in CloudWatch?"**
Use CloudWatch Logs Insights: `filter trace_id = "abc-123" | sort @timestamp asc` — same concept, managed query layer.
