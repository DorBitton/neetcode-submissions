# Observability

Metrics, logs, traces, and alerting. How you know your system is healthy.

The three pillars: **metrics** (what happened), **logs** (why it happened), **traces** (where it happened).

---

## Planned Topics

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | PromQL, log query patterns, key commands | ⬜ |
| `concepts/metrics.md` | Prometheus, metric types, PromQL, Grafana | ⬜ |
| `concepts/logging.md` | Structured logging, ELK vs Loki, log levels | ⬜ |
| `concepts/tracing.md` | Distributed tracing, Jaeger, OpenTelemetry | ⬜ |
| `concepts/alerting.md` | Alert design, on-call, runbooks | ⬜ |
| `concepts/aws-observability.md` | CloudWatch metrics/logs, X-Ray, Container Insights | ⬜ |
| `interview-questions.md` | 20 observability questions | ⬜ |

---

## On-prem vs AWS mapping (preview)

| On-prem | AWS |
|---|---|
| Prometheus + Grafana | CloudWatch + Managed Grafana |
| ELK / Loki | CloudWatch Logs |
| Jaeger | X-Ray |
| PagerDuty / OpsGenie | CloudWatch Alarms + SNS |
