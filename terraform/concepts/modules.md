# Terraform Modules

> Reusable building blocks. The difference between Terraform code that impresses and code that gets a flag.

---

## Table of Contents

1. [Why Modules Exist](#1-why-modules-exist)
2. [Module Structure](#2-module-structure)
3. [Calling a Module](#3-calling-a-module)
4. [Module Inputs and Outputs](#4-module-inputs-and-outputs)
5. [Module Sources and Versioning](#5-module-sources-and-versioning)
6. [Terraform Registry](#6-terraform-registry)
7. [Interview Questions](#7-interview-questions)

---

## 1. Why Modules Exist

Without modules, teams copy-paste infrastructure code between environments:

```
❌ The red flag pattern:
  environments/prod/main.tf     ← 300 lines of VPC + EC2 + ALB config
  environments/staging/main.tf  ← same 300 lines, slightly different values
  environments/dev/main.tf      ← same 300 lines again

  Result: bug in security group? Fix it in 3 places.
          Upgrade to t3.large? Edit 3 files.
          Add a new AZ? Touch 3 configs, hoping they stay in sync.
```

Modules solve this by separating **what** (the module) from **where** (the caller):

```
✅ The senior pattern:
  modules/vpc/         ← one definition of "how we build a VPC"
  modules/ec2-cluster/ ← one definition of "how we build an app cluster"

  environments/prod/main.tf     ← calls modules with prod values
  environments/staging/main.tf  ← calls same modules with staging values
  environments/dev/main.tf      ← calls same modules with dev values

  Fix bug in vpc module → fixed everywhere instantly.
```

**The interview answer:** "We wrap all reusable infrastructure patterns in modules — VPC layout, EC2 clusters, RDS setup. Environments call the same module with different inputs. That way a bug fix or upgrade is one change, not one per environment."

---

## 2. Module Structure

A module is just a directory with `.tf` files. Convention:

```
modules/
└── vpc/
    ├── main.tf        ← the actual resources
    ├── variables.tf   ← inputs the caller passes in
    ├── outputs.tf     ← values the caller gets back
    └── versions.tf    ← required Terraform and provider versions (optional)
```

**main.tf** — the resources:
```hcl
# modules/vpc/main.tf
resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name        = var.name
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]
  tags = {
    Name = "${var.name}-public-${count.index}"
  }
}
```

**variables.tf** — the inputs:
```hcl
# modules/vpc/variables.tf
variable "name" {
  description = "Name prefix for all resources"
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
}

variable "availability_zones" {
  type = list(string)
}

variable "environment" {
  type = string
}
```

**outputs.tf** — what the module exposes:
```hcl
# modules/vpc/outputs.tf
output "vpc_id" {
  value       = aws_vpc.this.id
  description = "The ID of the VPC"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "List of public subnet IDs"
}
```

---

## 3. Calling a Module

The caller passes in variable values and reads outputs:

```hcl
# environments/prod/main.tf
module "vpc" {
  source = "../../modules/vpc"    # local path

  name                = "prod"
  cidr_block          = "10.0.0.0/16"
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  availability_zones  = ["us-east-1a", "us-east-1b"]
  environment         = "prod"
}

# Use the module's output in another resource
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.large"
  subnet_id     = module.vpc.public_subnet_ids[0]   # module output
}

# Or pass to another module
module "app_cluster" {
  source         = "../../modules/ec2-cluster"
  vpc_id         = module.vpc.vpc_id               # module output
  subnet_ids     = module.vpc.public_subnet_ids    # module output
  instance_count = 3
}
```

Reference a module's output: `module.<module_name>.<output_name>`

---

## 4. Module Inputs and Outputs

### Inputs — variable types

```hcl
variable "name" {
  type = string
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "enable_monitoring" {
  type    = bool
  default = false
}

variable "allowed_cidrs" {
  type    = list(string)
  default = []
}

variable "tags" {
  type    = map(string)
  default = {}
}

# Object type — structured input
variable "database" {
  type = object({
    engine         = string
    instance_class = string
    multi_az       = bool
  })
}
```

### Validating inputs

```hcl
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod"
  }
}
```

### Sensitive outputs

```hcl
output "db_password" {
  value     = random_password.db.result
  sensitive = true   # won't print in terminal output, still in state file
}
```

---

## 5. Module Sources and Versioning

The `source` argument tells Terraform where to fetch the module from.

### Local path
```hcl
module "vpc" {
  source = "../../modules/vpc"
}
```

### Git repository
```hcl
module "vpc" {
  source = "git::https://github.com/myorg/terraform-modules.git//modules/vpc?ref=v1.2.0"
}
```

The `?ref=v1.2.0` pins to a specific git tag. Without `ref`, you get the default branch — dangerous in production because the module can change unexpectedly.

### Terraform Registry (public)
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"   # ~> means "5.x but not 6.0"
}
```

### Version constraints
```
= 5.0.0   exact version
!= 5.0.0  anything except
> 5.0.0   greater than
>= 5.0.0  greater than or equal
~> 5.0    any 5.x (patch and minor bumps OK, but not 6.0)
~> 5.0.0  any 5.0.x (only patch bumps OK)
```

**Rule:** always pin module versions in production. `~> 5.0` is a reasonable constraint — you get bug fixes automatically, but breaking changes (6.0) require an explicit update.

---

## 6. Terraform Registry

[registry.terraform.io](https://registry.terraform.io) hosts public, verified modules for common patterns.

**AWS-specific community modules** (the community-maintained terraform-aws-modules org):
```hcl
# VPC with public/private subnets, NAT gateways
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  name    = "my-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
}

# EKS cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"
  cluster_name = "my-cluster"
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.private_subnets
}
```

These registry modules wrap hundreds of AWS resources into a clean interface. They're production-ready, well-tested, and widely used at big tech companies. Reading their source is one of the best ways to learn advanced Terraform patterns.

---

## 7. Interview Questions

**"How do you avoid duplicating infrastructure code between environments?"**
> "We use modules. A module is a reusable directory of Terraform config that accepts input variables. Our environments each call the same module with different values — prod gets `instance_type = t3.large`, dev gets `t3.micro`. One module, no copy-paste."

**"What is a module output and how do you use it?"**
> "Outputs are values that a module exposes to its caller. For example, our VPC module outputs the VPC ID and subnet IDs. The EC2 module that runs in that VPC calls `module.vpc.vpc_id` to reference those outputs. This is how modules compose together — outputs of one become inputs to another."

**"How do you version your Terraform modules?"**
> "We keep shared modules in a separate git repo, tagged with semantic versions. Module callers pin to a specific tag using `?ref=v1.2.0`. That way a module change doesn't automatically affect production — callers opt in to upgrades. In practice we also use `~> 5.0` version constraints for public registry modules."

**"What's the difference between a module variable and a resource attribute?"**
> "A variable is an input the caller passes in — it's how you parameterize a module. A resource attribute is a property of a specific resource that Terraform either reads from state or computes after creation. Variables make modules reusable; outputs expose resource attributes to callers."
