# Scenario: AWS Cost Anomaly Detection

## Problem Statement (as interviewer would say it)

> "Your AWS bill spiked unexpectedly last month. Walk me through how you'd write a script to catch that automatically before the invoice lands."

---

## Clarifying Questions to Ask

- Which services do you want to monitor — all services or a specific subset (EC2, RDS, data transfer)?
- Is the alert threshold absolute (e.g., $500/day) or relative (e.g., 2x baseline)?
- Daily or weekly check cadence?
- Single AWS account or an AWS Organizations multi-account setup?

---

## Core Concept

AWS Cost Explorer API stores billing data queryable by time range and service. There is a **24-hour lag** — today's spend appears tomorrow. Unblended costs = what you actually pay on a single account (as opposed to blended costs, which average across reserved capacity in an org).

The approach: pull 30 days of daily cost data per service, build a 7-day rolling baseline per service, and flag any day where actual cost exceeds `baseline_avg + 2 * stdev`.

---

## Worked Solution

```python
#!/usr/bin/env python3
"""Detect daily AWS spend anomalies using a rolling 7-day baseline."""
import boto3, statistics, sys
from datetime import datetime, timedelta

def get_daily_costs(days=30):
    ce = boto3.client("ce", region_name="us-east-1")
    end = datetime.today().date() - timedelta(days=1)   # exclude today — 24h lag
    start = end - timedelta(days=days)
    r = ce.get_cost_and_usage(
        TimePeriod={"Start": str(start), "End": str(end)},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return r["ResultsByTime"]

def build_timeseries(results):
    """Reshape: {service: [{date, cost}, ...]}"""
    services = {}
    for day in results:
        date = day["TimePeriod"]["Start"]
        for g in day["Groups"]:
            svc = g["Keys"][0]
            cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
            services.setdefault(svc, []).append({"date": date, "cost": cost})
    return services

def detect_anomalies(services, baseline_days=7, multiplier=2.0):
    """Flag days where cost > baseline_avg + 2 standard deviations."""
    anomalies = []
    for svc, daily in services.items():
        if len(daily) < baseline_days + 1:
            continue
        for i in range(baseline_days, len(daily)):
            baseline = [d["cost"] for d in daily[i - baseline_days:i]]
            avg = statistics.mean(baseline)
            if avg < 0.01:
                continue                # skip near-zero services — noise only
            std = statistics.stdev(baseline) if len(baseline) > 1 else 0
            threshold = avg + multiplier * std
            if daily[i]["cost"] > threshold:
                anomalies.append({
                    "service": svc,
                    "date": daily[i]["date"],
                    "actual": round(daily[i]["cost"], 2),
                    "baseline_avg": round(avg, 2),
                    "pct_above": round((daily[i]["cost"] - avg) / avg * 100, 1),
                })
    return sorted(anomalies, key=lambda x: x["date"])

def main():
    print("Fetching 30 days of AWS costs (today excluded — 24h billing lag)...")
    results = get_daily_costs()
    services = build_timeseries(results)
    anomalies = detect_anomalies(services)

    if not anomalies:
        print("No anomalies detected.")
        return

    for a in anomalies:
        print(f"\nService: {a['service']}")
        print(f"Date:    {a['date']}")
        print(f"Actual:  ${a['actual']}  (baseline avg: ${a['baseline_avg']}, +{a['pct_above']}%)")

    print("\nNote: billing label is AWS attribution, not root cause.")
    print("Ask: what changed in infrastructure on or before the flagged date?")

if __name__ == "__main__":
    main()
```

---

## Key Insight to Say in the Interview

> "AWS billing labels are AWS's attribution, not a pointer to the resource. An EC2 spike could be EBS snapshot copies or cross-region data transfer. I'd start from what changed operationally on that date — not from the billing label."

---

## Follow-Up Q&A

**"How would you alert to Slack?"**
```python
import requests
requests.post(SLACK_WEBHOOK, json={"text": f"Cost spike: {a['service']} +{a['pct_above']}% on {a['date']}"})
```

**"How would you run this daily?"**
Cron: `0 9 * * * python3 cost_anomaly.py` — or EventBridge rule triggering a Lambda.

**"What's the difference between unblended and blended costs?"**
Unblended = what you actually pay. Blended = weighted average across org reserved capacity — only relevant in multi-account orgs where Reserved Instances are shared across accounts.

**"What if spend is consistently elevated?"**
The script uses a rolling baseline — it detects *sudden changes*, not elevated baselines. That's intentional: you don't want to alert on expected cost increases after a planned launch. A consistently elevated spend (no sudden change) would not fire.
