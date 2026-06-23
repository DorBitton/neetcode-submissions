# Study Roadmap — Senior SRE / DevOps

> **Open this when you don't know what to do next.**
> Work top to bottom. Finish a checkbox before moving to the next.

---

## Where you are right now

| Subject | Resource | Status |
|---|---|---|
| DSA | NeetCode + hellointerview.com | 🔄 In progress — binary search section |
| Linux | KillerCoda scenarios | 🔄 In progress — Pawel ✅ all 20, Alexis scenarios started |
| Networking | L3 ✅ L4 ✅ L7 🔄 | 🔄 In progress |
| Docker | KillerCoda scenarios | 🔄 In progress — fundamentals built, scenarios starting |
| Everything else | — | ⬜ Not started |

---

## Round 1 — Foundation
*Goal: be able to answer basic questions in every core area. Don't go deep yet.*

### DSA (ongoing — parallel with everything else)
- [ ] Complete all NeetCode Easy problems
- [ ] Reach 50% of NeetCode Medium (arrays, hashmaps, strings, two pointers, sliding window)
- [ ] Stop here for now — SRE interviews rarely go harder than medium

### Linux (in progress)
- [ ] Complete KillerCoda Linux scenarios by Pawel Piwosz (all of them)
- [ ] Complete KillerCoda Linux scenarios by Alexis Carbillet
- [ ] After each scenario: open `linux/` notes and fill in anything new you learned
- [ ] Answer all 25 questions in `linux/interview-questions.md` out loud without looking

### Networking — L3 / L4 / L7 (start after Linux feels solid)
- [x] Read `networking/concepts/l3-network-layer.md` — understand IP, CIDR, routing
- [x] Read `networking/concepts/l4-transport-layer.md` — understand TCP vs UDP, F5 vs NLB
- [ ] Read `networking/concepts/l7-application-layer.md` — understand HTTP, DNS, TLS, F5 vs ALB
- [ ] Read `networking/CHEATSHEET.md` and quiz yourself
- [ ] Answer all questions in `networking/interview-questions.md` out loud
- [ ] Find 1-2 YouTube SRE interview videos covering networking → extract patterns → add to `interview-prep/patterns/networking-patterns.md`

---

## Round 2 — Core SRE Stack
*Goal: be able to have a real technical conversation about each subject.*

### Docker
- [x] Found KillerCoda Docker scenarios (10 scenarios)
- [x] Read `docker/concepts/core-concepts.md` — containers vs VMs, images, layers, registries
- [ ] KillerCoda Group 1: Building, CMD/ENTRYPOINT, COPY/ADD, best practices, updating
- [ ] Read `docker/concepts/dockerfile.md`
- [ ] KillerCoda Group 2: Port forwarding, network drivers
- [ ] Read `docker/concepts/networking.md`
- [ ] KillerCoda Group 3: Volumes, bind mounts, env vars
- [ ] Read `docker/concepts/volumes.md`
- [ ] Be able to: write a Dockerfile, run a container, set up networking between containers, use volumes
- [ ] Answer `docker/interview-questions.md` out loud

### Kubernetes
- [ ] Work through a structured K8s course (KillerCoda has K8s scenarios too)
- [ ] Understand: pods, deployments, services, ingress, configmaps, secrets, RBAC
- [ ] Read `kubernetes/concepts/` alongside the course
- [ ] Read `aws/eks.md` — understand what EKS adds on top
- [ ] Answer `kubernetes/interview-questions.md` out loud

### AWS Core
- [ ] Networking first: VPC, subnets, route tables, security groups, NACLs
- [ ] Then: EC2, IAM roles and policies, S3, ALB/NLB
- [ ] Read `aws/concepts/networking/` — understand how it maps to on-prem networking
- [ ] Be able to draw a 3-tier architecture in AWS from memory
- [ ] Answer `aws/interview-questions.md` out loud

### Terraform
- [ ] Complete HashiCorp's free beginner tutorials (learn.hashicorp.com)
- [ ] Write Terraform to deploy a VPC + EC2 + security groups in AWS
- [ ] Read `terraform/concepts/` alongside the tutorial
- [ ] Answer `terraform/interview-questions.md` out loud

---

## Round 3 — Interview Ready
*Goal: be able to pass a senior SRE interview at big tech.*

### Python Scripting
- [ ] Write a script that calls the AWS API using boto3 (list EC2 instances, S3 buckets)
- [ ] Write a log parser: read a file, extract errors, count occurrences, output report
- [ ] Write a health check script: hit an HTTP endpoint, alert if down
- [ ] Read `scripting/concepts/` for patterns and built-ins

### Observability
- [ ] Understand Prometheus: metrics types (counter, gauge, histogram), PromQL basics
- [ ] Understand Grafana: dashboards, alerting
- [ ] Understand logging: structured logs, log levels, ELK vs Loki
- [ ] Map to AWS: CloudWatch metrics, CloudWatch Logs, X-Ray
- [ ] Read `observability/concepts/` and answer interview questions

### System Design + SRE Concepts
- [ ] Be able to design: URL shortener, rate limiter, notification system
- [ ] Understand: SLOs vs SLAs vs SLIs, error budgets, toil
- [ ] Understand: incident management, postmortems, on-call design
- [ ] Read `system-design/concepts/` and answer interview questions

### Interview Patterns
- [ ] Watch 3-5 YouTube SRE/DevOps interview recordings (real ones, not tutorials)
- [ ] Extract question patterns → add to `interview-prep/patterns/`
- [ ] Practice STAR answers for 10 behavioral questions in `interview-prep/behavioral.md`
- [ ] Do 2-3 mock system design interviews (with a peer or record yourself)

---

## Weekly rhythm

```
Main subject (1-2 hours/day):   hands-on practice (KillerCoda, writing code, deploying things)
Side subject (30 min/day):      read notes, watch one short video
DSA (30 min/day):               1-2 NeetCode problems, always ongoing
End of week:                    answer 5 interview questions out loud, update progress
```

**Rule:** Hands-on > reading notes > watching videos. In that order.

---

## Checkpoints — ask yourself these before moving to the next round

**After Round 1:**
- Can you navigate and troubleshoot a Linux system without googling basic commands?
- Can you explain what happens when you type a URL and hit enter (all layers)?
- Can you solve NeetCode medium array/hashmap problems consistently?

**After Round 2:**
- Can you deploy a containerized app to Kubernetes from scratch?
- Can you design and deploy a simple AWS VPC architecture with Terraform?
- Can you explain the difference between ALB and NLB and when to use each?

**After Round 3:**
- Can you pass a 45-minute system design interview for a distributed SRE-flavored problem?
- Can you answer "tell me about an incident you managed" with a real or realistic story?
- Can you write a Python script live in an interview to parse logs or call an API?
