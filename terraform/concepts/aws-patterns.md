# Terraform AWS Patterns — VPC, Modules, Networking

> The Terraform-specific implementation layer. For the underlying networking
> concepts (what a VPC/subnet/route table *is*, on-prem ↔ AWS mapping), see
> `networking/concepts/l3-network-layer.md` section 7 — this doc doesn't
> repeat that, it covers how you actually build it in HCL and the mistakes
> that show up doing it for real.

---

## Table of Contents

1. [AZ Discovery — Don't Hardcode Zone Names](#1-az-discovery--dont-hardcode-zone-names)
2. [Dynamic CIDR Math — `cidrsubnet()`](#2-dynamic-cidr-math--cidrsubnet)
3. [The `count` Gotcha — Lists, Indexing, Splat](#3-the-count-gotcha--lists-indexing-splat)
4. [NAT Gateway — Terraform-Specific Pitfalls](#4-nat-gateway--terraform-specific-pitfalls)
5. [Why Multi-AZ Matters Beyond "Terraform Made Me"](#5-why-multi-az-matters-beyond-terraform-made-me)
6. [Wiring Two Modules Together](#6-wiring-two-modules-together)
7. [Interview Questions](#7-interview-questions)

---

## 1. AZ Discovery — Don't Hardcode Zone Names

AZ letter-to-physical-datacenter mapping is randomized **per AWS account** (AWS spreads load evenly across accounts). Names like `us-east-1a` are stable and valid within your account, but hardcoding them ties your module to one region and isn't portable.

```hcl
data "aws_availability_zones" "available" {
  state = "available"
}
```

This queries AWS at plan time for whatever AZs actually exist in the configured region. Index into the result (`data.aws_availability_zones.available.names[0]`, `[1]`, ...) instead of typing literal zone names. Combine with `count.index % length(...)` when the number of subnets doesn't necessarily equal the number of AZs available — the modulo wraps around defensively instead of erroring on an out-of-range index.

---

## 2. Dynamic CIDR Math — `cidrsubnet()`

A tempting shortcut: build subnet CIDRs with string interpolation.

```hcl
# Fragile — only works because the VPC CIDR happens to divide neatly
# on the third octet. Breaks silently for a /20, a /26, anything else.
cidr_block = "10.0.${count.index}.0/24"
```

The correct, general tool is the built-in `cidrsubnet(prefix, newbits, netnum)` function — it mathematically carves a subnet out of a parent CIDR regardless of the parent's shape:

```hcl
cidr_block = cidrsubnet(var.vpc_cidr, 8, count.index)
# prefix = var.vpc_cidr (e.g. "10.0.0.0/16")
# newbits = 8  →  new mask = 16 + 8 = /24
# netnum = count.index  →  which /24 to return (0, 1, 2, ...)
```

**Real bug this catches:** if you split public and private subnets from the same CIDR range using two separate `count`-based resources, you need an *offset* so the ranges don't collide — e.g. private subnets start at `count.index + var.az_count` instead of `count.index`. If that offset is a hardcoded literal (`+ 2`) instead of driven by the same variable controlling the public subnet count, bumping `az_count` from 2 to 3 silently creates an overlapping CIDR block. Any offset math has to reference the same variable the other side's `count` uses.

---

## 3. The `count` Gotcha — Lists, Indexing, Splat

This is the single most common class of bug when writing modules with `count`, and it comes up repeatedly:

**The rule:** a resource with `count = N` isn't "a resource" — it's a **list** of N resources, indexed `[0]` through `[N-1]`. Anything referencing it must either index into a specific element (`aws_subnet.public[0].id`) or explicitly ask for the whole list via a **splat expression** (`aws_subnet.public[*].id`). A bare reference with no brackets (`aws_subnet.public.id`) only type-checks when the resource has *no* `count` at all.

```hcl
# BROKEN — aws_subnet.public has count, this has no index
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# FIXED — the association itself also needs count, paired index-for-index
resource "aws_route_table_association" "public" {
  count          = var.az_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
```

**Splat expressions in outputs** — when a module needs to hand back *every* id from a counted resource (e.g. all public subnet ids, for an ALB that attaches to all of them):

```hcl
output "public_subnet_ids" {
  value = aws_subnet.public[*].id   # list of every instance's id
}
```

**Dynamic vs. static pairing** — this bug also shows up between *two different* resources when only one of them has `count`. A NAT Gateway needs its own dedicated Elastic IP; you can't attach one static EIP to two counted NAT Gateway instances:

```hcl
# BROKEN — one EIP (no count), two NAT gateways both trying to use it
resource "aws_eip" "nat" {
  domain = "vpc"
}
resource "aws_nat_gateway" "nat" {
  count         = 2
  allocation_id = aws_eip.nat.id   # only one EIP exists — second NAT gateway fails
  subnet_id     = aws_subnet.public[count.index].id
}

# FIXED (if you actually want one NAT Gateway per AZ) — count matches, index matches
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"
}
resource "aws_nat_gateway" "nat" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}
```

The cheaper alternative — **one shared NAT Gateway** for all private subnets (single EIP, single NAT gateway, no `count` on either) — is a common real-world cost tradeoff: half the hourly NAT charge, at the cost of all private egress sharing one failure domain instead of being isolated per AZ.

---

## 4. NAT Gateway — Terraform-Specific Pitfalls

Beyond the EIP-pairing bug above:

- A NAT Gateway must sit in a **public** subnet (it needs its own route to the IGW to reach the internet) even though its purpose is serving **private** subnets.
- `depends_on = [aws_internet_gateway.igw]` on the NAT Gateway is the recommended explicit dependency in the AWS provider docs — Terraform can't always infer this ordering implicitly.
- Copying the official NAT Gateway example from the Terraform Registry docs and adapting it is a common source of a specific bug: the docs example names its own resources (commonly `example`, `web`, `lb`) and every cross-reference inside it uses those names. Renaming the resource declarations to match your own project without also renaming every reference to them (`aws_eip.example` → `aws_eip.nat`, etc.) leaves dangling references to resources that don't exist in your config. Always trace every reference in a copied example, not just the top-level resource name.

---

## 5. Why Multi-AZ Matters Beyond "Terraform Made Me"

An ALB has a hard AWS platform requirement: its subnets must span **at least 2 AZs**, full stop, regardless of how many backend instances exist. That's a mechanical requirement, not a design choice.

But the actual reliability reasoning goes further, and it's a genuinely common interview question ("walk me through what happens if an AZ goes down"): an AZ is a physically separate facility — independent power, cooling, network — so a failure in one doesn't take out the others (see `networking/concepts/l3-network-layer.md` for the on-prem parallel: this is the same reasoning behind redundant physical data centers with BGP/anycast between them). If your *backend instances* — not just the ALB's own nodes — all sit in one AZ's private subnet, an AZ failure takes your whole fleet down together even though the ALB itself survives (it has no healthy targets left to route to). Spreading even a small number of instances (2-3) across 2 AZs means an AZ failure only removes part of the fleet — this is exactly what SLO/error-budget tracking is meant to catch and measure.

---

## 6. Wiring Two Modules Together

Modules never reference each other directly — a `webcluster` module never writes `module.network...` inside its own files. All wiring happens **one level up**, in whichever root module calls both:

```hcl
# In the child module's variables.tf — it just declares what it needs
variable "private_subnet_ids" {
  type = list(string)
}

# In the ROOT module (e.g. envs/prod/main.tf) — this is where wiring happens
module "network" {
  source = "../../modules/network"
  # ...
}

module "webcluster" {
  source              = "../../modules/webcluster"
  private_subnet_ids  = module.network.private_subnet_ids   # output → input
  vpc_id              = module.network.vpc_id
}
```

Terraform infers the create-order automatically from this reference — no `depends_on` needed, since `webcluster`'s inputs reference `network`'s outputs.

**Two rules worth knowing cold:**

- **Only a root module can have a `backend` block.** State is per root-module invocation, not per child module. A child module shares whatever backend/state belongs to whichever root module is calling it — trying to put a `backend` block inside a child module is invalid.
- **A shared module has no state of its own** — it's just source code. If the same module (via a bare relative path, no version pin) is called from two independent root modules (e.g. `envs/prod` and `envs/stage`), editing the module doesn't change anything by itself. But the *next* `apply` in *either* root module picks up whatever the module's source currently looks like and diffs it against that environment's own state — meaning a change meant for staging can silently reach production the next time someone happens to run `apply` there, with no separate approval gate. This is exactly why teams pin shared modules to a version (`?ref=v1.2.0` for a git source, or a registry version constraint) instead of a bare path — see `concepts/modules.md` section 5.

---

## 7. Interview Questions

**"How do you avoid hardcoding availability zones in a Terraform module?"**
> "I use the `aws_availability_zones` data source to query what's actually available in the configured region at plan time, then index into that list. Hardcoding zone names like `us-east-1a` ties the module to one region/account — AZ letter-to-datacenter mapping is randomized per account by AWS."

**"Walk me through what happens if you reference a `count`-based resource without an index."**
> "A resource with `count` is a list, not a single resource. Terraform errors if you reference it without either picking a specific index (`resource[0]`) or using a splat expression (`resource[*].attribute`) to get every element. It's a common bug when wiring a counted resource's output into something else that also needs to be counted or otherwise indexed correctly."

**"Can a module have its own backend configuration?"**
> "No — only the root module you actually run `init`/`apply` in can define a backend. Child modules called via a `module` block share whatever state belongs to their caller. State isolation happens at the root-module level, not the module level."

**"What's the risk of sharing one module across multiple environments without version pinning?"**
> "The module itself has no state — editing its source doesn't do anything until someone runs `apply` in an environment that calls it. But with a bare path source, the *next* apply in any environment picks up whatever the module currently looks like on disk. A change tested only in staging can reach production on its next apply with no explicit approval step, unless the module is pinned to a version/git ref that each environment bumps deliberately."

**"Why does an ALB require subnets in at least 2 AZs, and why does that matter beyond satisfying the API?"**
> "AWS enforces it as a hard requirement because an ALB's own nodes are meant to survive an AZ failure. But it only pays off if your backend targets are also spread across those AZs — if the ALB spans 2 AZs but every instance sits in one of them, an AZ failure leaves the ALB standing with nothing healthy to route to."
