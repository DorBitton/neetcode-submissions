# System Design Interview Patterns (SRE Focus)

SRE system design questions are not the same as software engineering system design. They focus on **reliability, operability, and failure modes** — not just scalability.

---

## How SRE System Design Differs

Software eng: "Design Twitter's feed." → Data model, caching, sharding, API design.
SRE: "How would you make this system production-ready?" → SLOs, observability, failure modes, deployment strategy, incident response.

Know both angles. Big tech interviews often blend them.

---

## Pattern 1: SLOs / SLIs / Error Budgets

**They ask:** "How do you decide what reliability to target?"

**The framework:**

```
SLI  Service Level Indicator   — the metric you measure (request success rate, p99 latency)
SLO  Service Level Objective   — the target you commit to (99.9% success rate)
SLA  Service Level Agreement   — the external contract with consequences if broken
Error Budget = 100% - SLO      — how much failure you're allowed per month
```

**Why it matters for design:**
- If error budget is healthy → teams can ship fast, tolerate more risk
- If error budget is burned → freeze features, focus only on reliability

**Common SLOs:**
- 99.9% availability = 43 min downtime/month
- 99.99% = 4.3 min/month
- 99.999% = 26 sec/month

**What they listen for:** understanding that SLOs drive tradeoffs between velocity and reliability, not just "we aim for five nines."

---

## Pattern 2: Designing for Failure

**They ask:** "This system has a database. What happens when it goes down?"

**Answers they want:**

**Redundancy:**
- DB: Multi-AZ replica (RDS) or read replicas
- App tier: multiple instances, no single point of failure
- LB: managed service (ALB/NLB) has built-in HA

**Graceful degradation:**
- Can you serve cached data when DB is unavailable?
- Can you queue writes and process when DB recovers?
- What's the degraded UX? (feature off vs full outage)

**Circuit breakers:**
- Stop sending requests to a failing dependency
- Fail fast instead of piling up waiting requests
- Attempt recovery after a timeout window

**Timeouts everywhere:**
- Always set connect + read timeouts on external calls
- No timeout = threads pile up = cascading failure

---

## Pattern 3: Observability Design

**They ask:** "How would you monitor this system?"

**The three pillars:**

```
Metrics   → what's happening now (Prometheus + Grafana, CloudWatch)
Logs      → what happened in detail (ELK, Loki, CloudWatch Logs)
Traces    → why it's slow across services (Jaeger, X-Ray, Tempo)
```

**What to cover for any system:**
1. **Golden signals** (the four): latency, traffic, errors, saturation
2. **Alerting**: alert on SLO breach (burn rate alerts), not on every metric threshold
3. **Dashboards**: separate views for ops (is it broken now?) vs engineering (what caused it?)
4. **Log aggregation**: centralize, structured (JSON), indexed for searching

**Anti-pattern they watch for:** alert on CPU > 80% instead of on user-visible impact.

---

## Pattern 4: Incident Management

**They ask:** "Walk me through how you'd handle a major outage."

**The phases:**

1. **Detect:** alert fires → on-call gets paged (PagerDuty, OpsGenie)
2. **Acknowledge:** SLA on how fast you respond (typically 5 min)
3. **Coordinate:** declare incident severity, open war room (Slack channel), assign IC (Incident Commander)
4. **Communicate:** update status page, notify stakeholders — do NOT go silent
5. **Mitigate first:** rollback, failover, increase capacity — buy time before root cause
6. **Root cause:** now investigate WHY once users are unblocked
7. **Postmortem:** blameless, within 48-72 hours, document timeline + action items

**Severity levels (typical):**
- SEV1: full outage, revenue impact, all hands
- SEV2: significant degradation, some users impacted
- SEV3: minor issue, workaround available

---

## Pattern 5: Scaling Patterns

**They ask:** "How would you handle 10x traffic increase?"

**Horizontal vs vertical:**
- Vertical: bigger machine. Simple but hits limits and creates SPOF.
- Horizontal: more machines. Requires stateless app tier + shared state elsewhere.

**Layers to scale:**

```
DNS         →  Route53 latency routing, multiple regions
Load Balancer  →  ALB/NLB scale automatically (managed)
App tier    →  Auto Scaling Group based on CPU/custom metrics
Cache       →  ElastiCache (Redis/Memcached) to reduce DB load
Database    →  Read replicas for read-heavy; sharding for write-heavy
CDN         →  CloudFront to cache static assets and reduce origin load
```

**What they listen for:** understanding that you can't just scale one layer. Bottleneck shifts.

---

## Pattern 6: Deployment Architecture

**They ask:** "How would you deploy updates to this system safely?"

**What to cover:**
- Strategy: rolling, blue-green, canary (see kubernetes-patterns.md)
- Automated rollback trigger: error rate spike → auto rollback
- Feature flags: decouple deploy from release; turn features on gradually
- Health checks + readiness probes: don't send traffic to unhealthy instances
- Smoke tests post-deploy: automated test suite hits key user flows

**CI/CD pipeline shape:**
```
Code push → Build + Unit tests → Integration tests → Staging deploy → Canary 5% → Full rollout
```

Each gate blocks the next stage. Automatic rollback if error rate exceeds threshold.

---

## Structuring Your Answer (30-min design question)

1. **Clarify requirements (3-5 min)**
   - Scale: QPS, data volume, users
   - Consistency vs availability tradeoff
   - Read-heavy vs write-heavy
   - SLO target

2. **High-level design (5 min)**
   - Draw boxes: client → LB → app → cache → DB
   - Identify what component answers the core requirement

3. **Deep dive on components (15 min)**
   - Data model, API shape
   - Storage choices and why
   - Failure modes at each component

4. **Reliability and ops (5 min)**
   - SLOs, alerting, on-call considerations
   - How you'd deploy changes

5. **Wrap-up (2 min)**
   - Tradeoffs you made
   - What you'd do differently at higher scale
