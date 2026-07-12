# Terraform

Real hands-on Terraform, built for senior DevOps/SRE interview prep:
**[aws-web-cluster-slo](https://github.com/DorBitton/aws-web-cluster-slo)** —
an nginx web cluster on AWS (VPC, ALB, EC2), provisioned with Terraform,
configured with Ansible, deployed via GitHub Actions, with a custom Python
SLO/SLI pipeline measuring its own reliability. Hand-written line by line
with mentorship rather than following a tutorial — the mistakes made and
fixed along the way are the actual learning, documented below and in
`concepts/aws-patterns.md`.

## Architecture (current)

- VPC with public/private subnets split across 2 AZs, sized dynamically
  from a variable rather than hardcoded.
- Single NAT Gateway (cost-conscious choice over one-per-AZ) giving private
  subnets outbound access.
- ALB in the public subnets, fixed-count EC2 instances (no ASG — chosen
  deliberately so Ansible's inventory stays deterministic) in the private
  subnets.
- Remote state in S3, with a separate local-state "bootstrap" stack solving
  the chicken-and-egg problem of creating the bucket a backend would
  otherwise need to already exist.

Full status and directory layout: [infra/README.md in the project
repo](https://github.com/DorBitton/aws-web-cluster-slo/blob/master/infra/README.md).

## Best practices applied

- **Bootstrap chicken-and-egg solved correctly** — a separate root module
  with local state creates the S3 bucket; it's applied manually/rarely,
  never by CI, since a `backend` block reads state at `init` time and can't
  point at a bucket it's also responsible for creating.
- **Native S3 state locking** (`use_lockfile = true`, Terraform 1.10+) — no
  DynamoDB table needed.
- **Fully parameterized modules** — no hardcoded CIDRs, region names, or
  environment prefixes; every value that should vary by environment is a
  variable with a sane default.
- **Dynamic AZ discovery** via the `aws_availability_zones` data source —
  never hardcoded zone names, since AZ letter-to-datacenter mapping is
  randomized per AWS account.
- **`cidrsubnet()` for subnet math** instead of fragile string
  interpolation that only works for one particular CIDR shape.
- **No open SSH** — private instances reachable only via AWS Systems
  Manager Session Manager.
- **`.gitignore` from day one** — `.terraform/`, state files, and IDE
  config never enter git history.

## Outcomes / lessons worth remembering

The recurring bug, worth internalizing cold: **a resource with `count` is a
list, not a single resource.** Every reference to it needs an index
(`resource[0]`) or a splat (`resource[*].attribute`) — a bare `resource.id`
only works when there's no `count` at all. This hit the NAT Gateway/EIP
pairing, a route table association, and a module's outputs — more than
once. Full writeup with the actual broken/fixed code:
[`concepts/aws-patterns.md`](concepts/aws-patterns.md).

Second lesson: **only a root module can have a `backend` block.** A module
called via `module { source = ... }` shares whatever state belongs to its
caller — that's why `bootstrap` and `envs/prod` are each their own root
module, while `modules/network` and `modules/webcluster` are not. See
[`concepts/aws-patterns.md`](concepts/aws-patterns.md) section 6 and
[`concepts/state.md`](concepts/state.md) section 3.

## See also

| File | What's in it |
|---|---|
| `concepts/core-concepts.md` | Declarative vs imperative, init/plan/apply, providers, resources, variables, outputs |
| `concepts/state.md` | Local vs remote state, S3 backend, locking (DynamoDB + native), workspaces |
| `concepts/modules.md` | Module structure, inputs/outputs, versioning, registry |
| `concepts/aws-patterns.md` | VPC/subnet/AZ/NAT in Terraform, `count` + splat gotchas, module wiring — the real gotchas from this project |
