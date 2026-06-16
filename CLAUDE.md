# Claude Context — SRE / DevOps Interview Prep Repo

## Who this is for
Dor is preparing for **Senior DevOps / SRE roles at big tech companies** that run AWS and on-prem infrastructure. The target companies use hybrid infra: physical data centers (F5, BGP, bare metal) alongside AWS.

## Goal
Build a structured, reusable study and reference system covering the full SRE/DevOps interview stack. Not a tutorial — a knowledge base that grows as each subject is studied.

## Content philosophy — three layers on every topic
1. **Theory** — what it is, how it works, why it exists
2. **On-prem / real-world** — F5 load balancers, VIPs, BGP, bare metal, physical networking
3. **AWS equivalent** — the managed service that maps to the on-prem concept

This dual-track approach (on-prem + AWS) is what senior SRE interviewers at big tech expect. Example: load balancers → F5 VIP → pool → member on-prem, then ALB/NLB on AWS.

Cross-reference between subjects rather than duplicating content. For example, `aws/eks.md` covers what AWS adds on top of Kubernetes — it references `kubernetes/` for the core concepts rather than repeating them.

## Folder structure

| Folder | Purpose | Status |
|---|---|---|
| `Data Structures & Algorithms/` | NeetCode solutions — **DO NOT TOUCH** | Active (NeetCode automation) |
| `Data Structures & Algorithm Notes/` | DSA study notes — quick reference, patterns, data structures | Active |
| `linux/` | Linux commands, concepts, bash scripting, interview questions | Active |
| `networking/` | L3/L4/L7 focused — IP/routing, TCP/UDP, HTTP/DNS, load balancers | Next |
| `scripting/` | Python for SRE automation (boto3, subprocess, file I/O, CLI tools) | Skeleton |
| `docker/` | Containers, images, networking, volumes, compose | Skeleton |
| `kubernetes/` | K8s concepts, on-prem, RBAC, networking, EKS context | Skeleton |
| `terraform/` | IaC, state, providers, AWS modules | Skeleton |
| `aws/` | VPC, EC2, IAM, ALB/NLB, EKS, S3, Route53 | Skeleton |
| `observability/` | Prometheus, Grafana, logging stacks, alerting, CloudWatch | Skeleton |
| `system-design/` | Distributed systems, SLOs, reliability, incident management | Skeleton |
| `interview-prep/` | STAR behavioral answers, YouTube-extracted question patterns, roadmap | Active |

## Rules for agents working in this repo
- **Never touch** `Data Structures & Algorithms/` — managed by NeetCode automation
- **Never create a `_notes/` directory** — notes live inside each subject folder
- Each subject folder owns its own README, CHEATSHEET, `concepts/`, and `interview-questions.md`
- Write content lean — set up structure for future, write depth when the subject is actively being studied
- All networking/infrastructure examples must include both on-prem and AWS angles
- Prefer cross-referencing over duplicating content across folders

## Current progress
- ✅ Linux — foundation built, actively studying KillerCoda scenarios
- ✅ DSA — actively solving NeetCode problems via hellointerview.com
- 🔄 Networking — next subject (L3/L4/L7 structure created)
- ⬜ Scripting, Docker, Kubernetes, Terraform, AWS, Observability, System Design — skeleton only

## Resources in use
- DSA: [hellointerview.com](https://www.hellointerview.com/)
- Linux: [killercoda.com/linux](https://killercoda.com/linux) — Pawel Piwosz + Alexis Carbillet scenarios
- Interview patterns: YouTube SRE/DevOps interview recordings → extracted to `interview-prep/patterns/`

## Study approach
Round-based, not sequential. See `ROADMAP.md` for the full plan.
