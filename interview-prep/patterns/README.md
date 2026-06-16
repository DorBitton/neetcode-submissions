# Interview Question Patterns

Extracted from real SRE / DevOps interview recordings and experiences.

---

## How to add patterns

1. Watch a YouTube SRE/DevOps interview recording
2. Note every question asked (even paraphrased)
3. Note what a strong answer looked like vs a weak one
4. Add to the relevant file below

---

## Pattern Files

| File | Status |
|---|---|
| [`aws-patterns.md`](./aws-patterns.md) | ✅ VPC design, IAM, HA, debugging, security |
| [`kubernetes-patterns.md`](./kubernetes-patterns.md) | ✅ CrashLoopBackOff, deployments, RBAC, probes, EKS |
| [`terraform-patterns.md`](./terraform-patterns.md) | ✅ State, modules, plan/apply, errors, secrets |
| [`system-design-patterns.md`](./system-design-patterns.md) | ✅ SLOs, failure modes, observability, scaling, deployment |
| `linux-patterns.md` | ⬜ Not started |
| `networking-patterns.md` | ⬜ Not started |
| `docker-patterns.md` | ⬜ Not started |
| `behavioral-patterns.md` | ⬜ Not started |

---

## Format for each pattern entry

```markdown
## Source
[Video title](URL) — timestamp if relevant

## Questions asked
- Q1: exact or paraphrased question
- Q2: follow-up question
- Q3: follow-up question

## What a strong answer covered
- point 1
- point 2

## What tripped the candidate up
- point

## Maps to
- `networking/concepts/l4-transport-layer.md#tcp`
```
