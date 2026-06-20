# Terraform Core Concepts

> Declarative IaC. You describe what you want. Terraform figures out how to get there.

---

## Table of Contents

1. [Declarative vs Imperative](#1-declarative-vs-imperative)
2. [HCL Syntax](#2-hcl-syntax)
3. [Providers](#3-providers)
4. [Resources](#4-resources)
5. [Variables and Outputs](#5-variables-and-outputs)
6. [The Core Workflow](#6-the-core-workflow)
7. [State (overview)](#7-state-overview)

---

## 1. Declarative vs Imperative

This is the concept interviewers probe first.

**Imperative (Ansible, shell scripts):** you write the steps.
```bash
# Step 1: create security group
# Step 2: launch instance
# Step 3: wait for it to start
# Step 4: if instance already exists, skip step 2
```
The script says HOW. You are responsible for all the branching logic — "if it already exists, don't create it again."

**Declarative (Terraform):** you describe the end state.
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
}
```
Terraform figures out HOW. If the instance doesn't exist → create it. If it already exists with these settings → do nothing. If the AMI changed → recreate it. You describe what you want. Safe to run twice.

**The interview answer:** "Terraform is declarative — I describe the desired end state and Terraform diffs that against what currently exists, then makes the minimal changes to get there. This is safer than imperative scripts because there's no 'if already exists' logic for me to get wrong."

---

## 2. HCL Syntax

HCL (HashiCorp Configuration Language) is Terraform's syntax. It compiles to JSON under the hood.

### Basic block structure
```hcl
<block_type> "<type>" "<name>" {
  argument = value
}
```

### Key block types
```hcl
# Provider: tell Terraform which cloud/service you're using
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Resource: the thing you want to create
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name"
}

# Variable: an input parameter
variable "environment" {
  description = "dev, staging, or prod"
  type        = string
  default     = "dev"
}

# Output: a value to expose after apply
output "bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}

# Data source: read existing infrastructure (don't create it)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

### Reference syntax
```hcl
# Reference a resource attribute: <resource_type>.<name>.<attribute>
resource "aws_instance" "web" {
  subnet_id = aws_subnet.public.id   # reference another resource
  ami       = data.aws_ami.amazon_linux.id  # reference a data source
}

# Reference a variable: var.<name>
resource "aws_s3_bucket" "logs" {
  bucket = "logs-${var.environment}"   # string interpolation
}
```

---

## 3. Providers

Providers are plugins that know how to talk to a specific API — AWS, GCP, Azure, Kubernetes, etc.

```hcl
provider "aws" {
  region = "us-east-1"
}
```

Terraform downloads the provider during `terraform init`. Each provider version is locked in `.terraform.lock.hcl` — commit this to source control.

**Multi-region pattern:**
```hcl
provider "aws" {
  region = "us-east-1"
  alias  = "east"
}

provider "aws" {
  region = "us-west-2"
  alias  = "west"
}

resource "aws_s3_bucket" "west_bucket" {
  provider = aws.west
  bucket   = "my-west-bucket"
}
```

---

## 4. Resources

Resources are the things Terraform creates, updates, or deletes.

```hcl
resource "<provider>_<type>" "<local_name>" {
  # configuration
}
```

**Real example — EC2 in a VPC:**
```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name        = "main-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id   # implicit dependency
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public.id  # implicit dependency on subnet
}
```

**Implicit dependencies:** when you reference `aws_vpc.main.id` inside another resource, Terraform automatically knows to create the VPC first. You rarely need `depends_on` (explicit dependency).

---

## 5. Variables and Outputs

### Variables
```hcl
# Declaration
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/8"]
}
```

**Setting variable values (in priority order):**
```
1. Command line:   terraform apply -var="instance_type=t3.large"
2. terraform.tfvars file (auto-loaded)
3. *.auto.tfvars files
4. Environment variables: TF_VAR_instance_type=t3.large
5. Default value in declaration
```

**terraform.tfvars (the standard way):**
```hcl
# terraform.tfvars
instance_type = "t3.large"
environment   = "prod"
```

### Outputs
```hcl
# What to expose after apply
output "instance_public_ip" {
  value       = aws_instance.web.public_ip
  description = "Public IP of the web instance"
}

output "vpc_id" {
  value = aws_vpc.main.id
}
```

See outputs after apply:
```bash
terraform output
terraform output instance_public_ip
```

Outputs are also how **modules** return values to their callers.

---

## 6. The Core Workflow

```
terraform init     → download providers + modules, initialize backend
terraform plan     → show what changes would be made (dry run, no changes applied)
terraform apply    → make the changes (prompts for confirmation)
terraform destroy  → delete everything Terraform manages
```

### terraform init
```bash
terraform init
# Downloads: provider plugins (.terraform/providers/)
#            modules (.terraform/modules/)
#            configures the backend (where state is stored)
```
Run this once when you first clone a project, and again whenever you add providers or modules.

### terraform plan
```bash
terraform plan
terraform plan -out=tfplan   # save the plan to apply later
```

Output legend:
```
+ create      → new resource
~ update      → modify existing resource (in-place)
-/+ replace   → destroy and recreate (watch for this — causes downtime)
- destroy     → delete the resource
```

Always read the plan before applying. The `-/+ replace` annotation is where outages happen — if Terraform wants to replace a running instance, that means downtime unless you've planned for it.

### terraform apply
```bash
terraform apply             # prompts for yes/no
terraform apply -auto-approve  # skip prompt (use in CI, not manually)
terraform apply tfplan      # apply a saved plan (ensures exactly what you reviewed runs)
```

### terraform destroy
```bash
terraform destroy           # destroys everything in the state
terraform destroy -target aws_instance.web  # destroy one specific resource
```

---

## 7. State (overview)

Terraform tracks what it has created in a **state file** (`terraform.tfstate`). On every plan/apply, Terraform:
1. Reads the state file (what currently exists, according to Terraform)
2. Calls the cloud API to get the real current state
3. Diffs against your configuration
4. Makes the minimum changes needed

**The problem with local state:** if `terraform.tfstate` lives on your laptop, your teammate can't run Terraform — they don't have the state file. If they do run it, two copies of state diverge and you have a mess.

For team use and production, always use remote state. See `concepts/state.md`.
