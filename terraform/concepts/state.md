# Terraform State

> The most important interview topic for Terraform. Remote state + locking = team-safe infra.

---

## Table of Contents

1. [What State Is](#1-what-state-is)
2. [The Local State Problem](#2-the-local-state-problem)
3. [Remote State — S3 Backend](#3-remote-state--s3-backend)
4. [State Locking — DynamoDB](#4-state-locking--dynamodb)
5. [State Isolation](#5-state-isolation)
6. [Common State Commands](#6-common-state-commands)
7. [Interview Questions](#7-interview-questions)

---

## 1. What State Is

Terraform needs to know what it has already created. It can't just ask AWS "did you create this?" — AWS has no concept of Terraform resources, only raw AWS resources.

The state file (`terraform.tfstate`) is Terraform's mapping between:
```
Terraform config           →    Real AWS resource
"aws_instance.web"         →    i-0abc123def456 in us-east-1
"aws_vpc.main"             →    vpc-0xyz789 in us-east-1
```

On every `plan` or `apply`:
1. Terraform reads state → knows what it thinks exists
2. Terraform calls AWS API → knows what actually exists
3. Terraform reads your config → knows what you want
4. Terraform computes the diff between (3) and the union of (1)+(2)

Without state, Terraform would try to create everything fresh every time.

The state file is JSON:
```json
{
  "resources": [
    {
      "type": "aws_instance",
      "name": "web",
      "instances": [
        {
          "attributes": {
            "id": "i-0abc123def456",
            "instance_type": "t3.micro",
            "public_ip": "54.123.45.67"
          }
        }
      ]
    }
  ]
}
```

---

## 2. The Local State Problem

By default, state is stored locally as `terraform.tfstate` in the project directory.

**Why this is a red flag in interviews:**

```
Problem 1 — No sharing
  Alice runs terraform apply → state on Alice's laptop
  Bob tries to run terraform apply → has no state file
  Bob's apply creates duplicate resources (Terraform thinks nothing exists)

Problem 2 — No locking
  Alice and Bob both run terraform apply at the same time
  Both read the same (old) state, both make changes
  Second apply overwrites the state from the first
  Resources exist that no longer match state → "drift"

Problem 3 — Committed to git
  Some teams commit terraform.tfstate to source control
  State files contain sensitive values in plaintext (database passwords, private keys)
  Anyone with repo access sees all secrets
  Merge conflicts on a binary/JSON file = a nightmare
```

**The interview answer to avoid:** "We keep our state file in the repo."

---

## 3. Remote State — S3 Backend

Store state in S3 instead of locally. All teammates share the same state.

### Setup

Step 1 — Create the S3 bucket and DynamoDB table (do this manually once, or with a bootstrap Terraform config):
```bash
aws s3api create-bucket \
  --bucket my-terraform-state-prod \
  --region us-east-1

aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

Step 2 — Configure the backend in `main.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-prod"
    key            = "prod/vpc/terraform.tfstate"   # path within bucket
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"          # for locking
    encrypt        = true                            # encrypt at rest
  }
}
```

Step 3 — Run `terraform init` to migrate local state to S3:
```bash
terraform init
# Terraform will ask: "Do you want to copy existing state to the new backend?" → yes
```

### What changes with remote state

```
Before (local):
  terraform apply → writes tfstate to ./terraform.tfstate

After (S3 backend):
  terraform apply → reads state from S3
                  → acquires lock in DynamoDB
                  → makes changes
                  → writes new state to S3
                  → releases lock
```

No more laptop-specific state. Any teammate can run `terraform plan` and see the current state.

### S3 bucket configuration you should enable

```hcl
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

Versioning: if you mess up state (bad apply, corrupted file), you can roll back to a previous version. Essential for production.

---

## 4. State Locking — DynamoDB

Two people running `terraform apply` at the same time will corrupt state. Locking prevents this.

When Terraform starts a plan/apply, it writes a lock to DynamoDB:
```
LockID: "my-terraform-state-prod/prod/vpc/terraform.tfstate"
Info:    {"Operation": "OperationTypeApply", "Who": "alice@company.com"}
```

If someone else tries to run apply while the lock is held:
```
Error: Error acquiring the state lock

  Error message: ConditionalCheckFailedException: The conditional request failed
  Lock Info:
    ID:        abc123
    Path:      my-terraform-state-prod/prod/vpc/terraform.tfstate
    Operation: OperationTypeApply
    Who:       alice@company.com
    Created:   2024-01-15 14:23:11.123456789 +0000 UTC
```

They have to wait for Alice to finish. No concurrent applies possible.

**Breaking a stale lock** (if someone's process died and left a lock behind):
```bash
terraform force-unlock <LOCK_ID>
# Only do this if you are certain no apply is actually running
```

---

## 5. State Isolation

Running `terraform apply` in one environment shouldn't risk breaking another. Two approaches:

### Option A — Directory structure (recommended for most teams)

```
terraform/
├── environments/
│   ├── prod/
│   │   ├── main.tf       # uses module
│   │   ├── variables.tf
│   │   └── backend.tf    # s3 key = "prod/terraform.tfstate"
│   ├── staging/
│   │   ├── main.tf
│   │   └── backend.tf    # s3 key = "staging/terraform.tfstate"
│   └── dev/
│       ├── main.tf
│       └── backend.tf    # s3 key = "dev/terraform.tfstate"
└── modules/
    └── vpc/              # shared module
```

Each environment is a separate Terraform working directory with its own state file. Running apply in `prod/` is completely isolated from `staging/`.

### Option B — Workspaces

Workspaces allow multiple state files within a single working directory.

```bash
terraform workspace new prod
terraform workspace new staging
terraform workspace select prod
terraform workspace list
```

The state file path becomes: `s3://my-bucket/env:/<workspace>/terraform.tfstate`

**Workspace gotcha:** workspaces share the same configuration code — you have to use `terraform.workspace` to differentiate:
```hcl
resource "aws_instance" "web" {
  instance_type = terraform.workspace == "prod" ? "t3.large" : "t3.micro"
}
```

This gets messy fast. For environments with meaningful differences, directory structure is cleaner. Use workspaces for lightweight isolation (e.g., per-developer sandboxes).

---

## 6. Common State Commands

```bash
# List all resources in state
terraform state list

# Show details of a specific resource
terraform state show aws_instance.web

# Remove a resource from state without destroying it
# (useful when you want to "forget" about a resource but not delete it)
terraform state rm aws_instance.web

# Import an existing resource into state
# (bring a manually-created resource under Terraform management)
terraform import aws_instance.web i-0abc123def456

# Move a resource in state (rename in config without destroying)
terraform state mv aws_instance.web aws_instance.app

# Pull current state from remote and print it
terraform state pull

# Push a local state file to remote (danger — use carefully)
terraform state push
```

---

## 7. Interview Questions

**"Where do you store your Terraform state?"**
> "In S3 with versioning enabled so we can roll back to previous state files. We use a DynamoDB table for locking so concurrent applies are blocked. Each environment (dev, staging, prod) has its own state file path in the bucket."

**"What happens if two people run terraform apply at the same time?"**
> "With local state: race condition, second apply overwrites the first, state gets corrupted. With DynamoDB locking: the second apply immediately fails with a lock error and shows who holds the lock. Only one apply can run at a time."

**"What's in the state file?"**
> "It's a JSON map between Terraform resource names and real infrastructure IDs. Also contains attribute values — including sensitive ones like passwords and keys in plaintext, which is why we encrypt the S3 bucket and never commit state to git."

**"What is 'state drift' and how do you detect it?"**
> "Drift is when real infrastructure diverges from what's in state — someone made a manual change in the console. `terraform plan` detects it: Terraform refreshes state from the real API and shows a diff. We run `terraform plan` in CI on a schedule to catch drift before it causes problems."
