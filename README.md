# SRE / DevOps Interview Prep

Structured study repo for Senior SRE / DevOps roles at big tech companies.

> **Lost? Open [`ROADMAP.md`](./ROADMAP.md) — it tells you exactly what to do next.**

---

## Subjects

| Folder | What's in it | Status |
|---|---|---|
| [`Data Structures & Algorithms/`](./Data%20Structures%20&%20Algorithms/) | NeetCode solutions (auto-managed, do not touch) | 🔄 Active |
| [`Data Structures & Algorithm Notes/`](./Data%20Structures%20&%20Algorithm%20Notes/) | DSA quick reference, patterns, data structures | 🔄 Active |
| [`linux/`](./linux/) | Commands, concepts, bash, 25 interview questions | 🔄 Active |
| [`networking/`](./networking/) | L3/L4/L7 — IP, TCP, HTTP, DNS, load balancers (F5 + AWS) | ⬜ Next |
| [`scripting/`](./scripting/) | Python for SRE automation — boto3, subprocess, CLI tools | ⬜ Skeleton |
| [`docker/`](./docker/) | Containers, images, networking, volumes, compose | ⬜ Skeleton |
| [`kubernetes/`](./kubernetes/) | K8s concepts, RBAC, networking, EKS | ⬜ Skeleton |
| [`terraform/`](./terraform/) | IaC, state, AWS provider, modules | ⬜ Skeleton |
| [`aws/`](./aws/) | VPC, EC2, IAM, ALB/NLB, EKS, S3, Route53 | ⬜ Skeleton |
| [`observability/`](./observability/) | Prometheus, Grafana, logging, alerting, CloudWatch | ⬜ Skeleton |
| [`system-design/`](./system-design/) | Distributed systems, SLOs, reliability, incident mgmt | ⬜ Skeleton |
| [`interview-prep/`](./interview-prep/) | STAR behavioral, question patterns, resources | 🔄 Active |

---

## How content is structured

Every subject folder follows the same pattern:

```
subject/
├── README.md               ← progress tracker + file map
├── CHEATSHEET.md           ← one-page quick reference (open during review)
├── concepts/               ← deep-dive notes per topic
└── interview-questions.md  ← Q&A to practice out loud
```

Every technical topic covers **three layers**: theory → on-prem / real-world → AWS equivalent.
