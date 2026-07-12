# Terraform

Infrastructure as Code. Write infrastructure in HCL, version it, apply it.

---

## The lean learning path

This is the fastest path from zero to "I can talk about Terraform in an SRE interview":

### Phase 1 — Get the mental model (1 day)
Understand **declarative vs imperative** before touching any code. Terraform is declarative — you describe the end state, not the steps to get there. This is the concept interviewers probe most. See `concepts/core-concepts.md`.

### Phase 2 — Official tutorials (2-3 days)
[developer.hashicorp.com/terraform/tutorials/aws-get-started](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)

Do the AWS track only. Skip courses. Do these specific tutorials:
- "Build infrastructure" → init / plan / apply
- "Change infrastructure" → what happens when you modify a resource
- "Destroy infrastructure" → terraform destroy
- "Define input variables" → variables and tfvars
- "Query data with outputs" → output values

That's it for Phase 2. Stop there.

### Phase 3 — Book chapters 2, 3, 4 (1 week)
"Terraform Up and Running" by Yevgeniy Brikman. Only three chapters matter for interviews:

| Chapter | Topic | Why it matters |
|---|---|---|
| Chapter 2 | Core concepts + first real deployment | EC2 + security groups, variables, outputs |
| Chapter 3 | Remote state | **The most important interview topic.** S3 + DynamoDB locking. |
| Chapter 4 | Modules | Removes the copy-paste red flag from your answers |

Chapters 5-10 are reference material — read when you need them while building projects.

> Book is at `C:\Users\dbitt\Downloads\O'Reilly - Terraform Up & Running` (local only, not in repo).

### Phase 4 — Build something real (in progress)
Standalone capstone repo: `~/Documents/aws-web-cluster-slo` — an nginx web cluster on AWS (VPC, ALB, EC2), Terraform + Ansible + Python SLO scripts + GitHub Actions, built hand-written with mentorship rather than following a tutorial. `concepts/aws-patterns.md` documents the real gotchas hit while building its network module — that's the better proof of understanding than the Cloud Resume Challenge below, since it forces working through the mistakes yourself instead of following steps.

Cloud Resume Challenge (cloudresumechallenge.dev) remains a fine alternative/additional capstone if you want a second project:
- Build a static resume site + serverless backend manually first
- Then destroy it and rebuild the entire thing with Terraform
- The contrast between "clicking in console" and "terraform apply" is what makes it click

---

## Red flags interviewers watch for

These two answers immediately signal a junior-level Terraform user:

1. **"I have a terraform.tfstate file in my git repo"** → Local state committed to source control. Anyone on the team could run `apply` and overwrite it. See `concepts/state.md`.

2. **"I copy the code between environments"** → Not using modules. Copy-paste means bugs get copied too and updates require editing in multiple places. See `concepts/modules.md`.

Flip these: lead with "we use S3 remote state with locking" (DynamoDB table, or native `use_lockfile` on Terraform 1.10+ — know both) and "we wrap reusable infra in modules" and you sound senior.

---

## File Map

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | All commands + HCL syntax quick reference | ⬜ |
| `concepts/core-concepts.md` | Declarative vs imperative, init/plan/apply, providers, resources, variables, outputs | ✅ |
| `concepts/state.md` | Local vs remote state, S3 backend, DynamoDB locking, workspaces | ✅ |
| `concepts/modules.md` | Module structure, inputs/outputs, versioning, registry | ✅ |
| `concepts/aws-patterns.md` | VPC/subnet/AZ/NAT in Terraform, `count` + splat gotchas, module wiring | ✅ |
| `interview-questions.md` | 15 Terraform questions with answers | ⬜ |

---

## Resources

- **Official tutorials:** [developer.hashicorp.com/terraform/tutorials/aws-get-started](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)
- **Book:** "Terraform Up and Running" — Yevgeniy Brikman (O'Reilly). Chapters 2, 3, 4.
- **Cloud Resume Challenge:** [cloudresumechallenge.dev](https://cloudresumechallenge.dev)
- **Terraform Registry:** [registry.terraform.io](https://registry.terraform.io) — public modules and providers
