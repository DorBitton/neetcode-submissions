# Scenario: Canary Rollback

## Problem Statement (verbatim)

> "You deploy a new version to 20% of traffic. Error rate stays at 0%. But users are complaining about slow responses. Your automation doesn't roll it back. Why not, and how do you fix it?"

---

## Clarifying Questions to Ask

1. What signals does the current automation watch — error rate only, or latency too?
2. Is Prometheus available? What metrics does the app expose?
3. What's the acceptable P99 latency (your SLO)?
4. How many consecutive bad checks are required before rollback triggers?

---

## Core Concept

**Canary deployment:** send a small percentage of traffic (20%) to the new version first. Watch signals. Auto-rollback if a signal breaches its threshold before promoting to 100%.

**The bug:** automation watched *only error rate*. The canary was slow (5s P99) but returned HTTP 200 — error rate = 0%, rollback never triggered. Users felt the slowness; automation saw nothing wrong.

**The fix:** watch both error rate AND P99 latency. A service can be failing users without producing a single 5xx.

---

## v1 — Watches Error Rate Only (the broken version)

```bash
#!/usr/bin/env bash
# canary_watch_v1.sh — BROKEN: misses latency degradation
set -euo pipefail

PROMETHEUS="http://localhost:9090"
DEPLOYMENT="myapp-canary"
ERROR_THRESHOLD="0.05"
STRIKE_LIMIT=3
strikes=0

while true; do
    error_rate=$(curl -sf "$PROMETHEUS/api/v1/query" \
        --data-urlencode 'query=sum(rate(http_requests_total{app="myapp-canary",status=~"5.."}[1m])) / sum(rate(http_requests_total{app="myapp-canary"}[1m]))' \
        | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['data']['result']; print(r[0]['value'][1] if r else '0')" 2>/dev/null)
    error_rate="${error_rate:-0}"

    breach=$(echo "$error_rate > $ERROR_THRESHOLD" | bc -l)
    echo "[$(date -u +%T)] error_rate=${error_rate} breach=$([ "$breach" = "1" ] && echo YES || echo NO)"

    if [ "$breach" = "1" ]; then
        strikes=$((strikes + 1))
        [ "$strikes" -ge "$STRIKE_LIMIT" ] && { kubectl rollout undo deployment/"$DEPLOYMENT"; exit 0; }
    else
        strikes=0
    fi
    sleep 15
done
# With latency injection: error_rate=0 breach=NO — never rolls back. Users wait 5s per request.
```

---

## v2 — Watches Error Rate AND P99 Latency (the fix)

```bash
#!/usr/bin/env bash
# canary_watch_v2.sh — correct: watches both signals
set -euo pipefail

PROMETHEUS="http://localhost:9090"
DEPLOYMENT="myapp-canary"
ERROR_THRESHOLD="0.05"
LATENCY_THRESHOLD="2.0"      # P99 latency SLO in seconds
STRIKE_LIMIT=3
strikes=0

query_prometheus() {
    # Reusable helper — avoids repeating curl + python parse for every metric
    curl -sf "$PROMETHEUS/api/v1/query" --data-urlencode "query=$1" \
        | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['data']['result']; print(r[0]['value'][1] if r else '0')" 2>/dev/null
}

while true; do
    # Error rate: fraction of 5xx responses over the last 1 minute
    error_rate=$(query_prometheus \
        'sum(rate(http_requests_total{app="myapp-canary",status=~"5.."}[1m])) / sum(rate(http_requests_total{app="myapp-canary"}[1m]))')

    # P99 latency: requires histogram_quantile — app must expose _bucket metrics
    latency=$(query_prometheus \
        'histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{app="myapp-canary"}[1m])) by (le))')

    error_rate="${error_rate:-0}"
    latency="${latency:-0}"

    # Evaluate each signal independently — either can trigger rollback
    error_breach=$(echo "$error_rate > $ERROR_THRESHOLD" | bc -l)
    latency_breach=$(echo "$latency > $LATENCY_THRESHOLD" | bc -l)

    # Build a human-readable trigger label for the log line
    trigger=""
    [ "$error_breach" = "1" ] && trigger="error_rate(${error_rate})"
    [ "$latency_breach" = "1" ] && trigger="${trigger:+${trigger}, }latency_p99(${latency}s)"

    echo "[$(date -u +%T)] error_rate=${error_rate} latency_p99=${latency}s breach=${trigger:-none}"

    if [ "$error_breach" = "1" ] || [ "$latency_breach" = "1" ]; then
        strikes=$((strikes + 1))
        echo "  Strike ${strikes}/${STRIKE_LIMIT} — ${trigger}"
        if [ "$strikes" -ge "$STRIKE_LIMIT" ]; then
            echo "  ROLLBACK TRIGGERED — signal: ${trigger}"
            kubectl rollout undo deployment/"$DEPLOYMENT"
            exit 0
        fi
    else
        # Reset on a clean check — must be *consecutive* bad checks to trigger
        strikes=0
    fi
    sleep 15
done
```

---

## The Three-Strike Rule — How to Explain It

> One bad check doesn't trigger rollback — that's flap protection. A single spike in latency (GC pause, cold pod, noisy neighbor) shouldn't roll back a deployment. Three consecutive checks × 15s interval = 45 seconds of sustained degradation before rollback fires. Tune to your SLO: a tighter SLO means a lower `STRIKE_LIMIT` or shorter sleep. The tradeoff is false-positive rollbacks vs. time-to-rollback.

---

## Key Insight / Phrase to Say in the Interview

> "Automation is only as good as what it watches. Error rate 0% can coexist with P99 latency 5 seconds. Both are user-visible signals. A script that watches only errors is half-blind — it will miss any degradation that doesn't produce explicit failures. That's exactly what happened here."

---

## Follow-Up Q&A

**"How do you avoid false positive rollbacks?"**
Tune thresholds to match your baseline P99 (not a round number). Increase `STRIKE_LIMIT`. Watch P99 not P100 — outliers skew P100 and make it noisy. Add a minimum request rate guard: don't evaluate latency if fewer than N requests/min are flowing (low-traffic math is unreliable).

**"What's the difference between rollback and rollforward?"**
Rollback: revert to the previous known-good version. Rollforward: ship a new hotfix version past the broken one. For a broken canary at 20%, rollback is usually safer and faster. Rollforward makes sense when you can't revert (schema migration already ran, or rollback breaks something else).

**"What other signals would you watch?"**
Error budget burn rate (SLO-aware alerting), DB connection pool exhaustion (connections at max), memory trending up (potential OOM before it crashes), saturation metrics (queue depth, thread pool). Signals depend on what the service actually does — a data pipeline cares about throughput; an API cares about latency.

**"What if Prometheus is down?"**
The script currently defaults empty results to `0` — which is interpreted as "no breach." Prometheus unavailability silently looks like a clean canary. Fix: treat a Prometheus query failure as a warning signal, increment a separate `prometheus_failures` counter, and page/alert if unavailability persists. Don't auto-rollback on monitoring failure alone — that's too noisy — but don't silently ignore it either.

**"Why P99 and not average latency?"**
Average latency hides tail behavior. A service where 99% of requests take 10ms and 1% take 10s has a "great" average but terrible P99. SLOs are usually defined at P99 or P99.9 because that's the experience of real users at the tail, not the median user. Average is a vanity metric for latency.
