# Terraform Interview Patterns

Common patterns from real DevOps/SRE interviews.

---

## Pattern 1: State Questions

**They ask:** "What is Terraform state and why does it matter?"

**What they want to hear:**
- State is Terraform's record of what infrastructure exists and what it manages
- Without state, Terraform can't know what to create vs what to update vs what to delete
- Local state (`terraform.tfstate`) is fine for personal use; never use local state in teams
- Remote state: S3 + DynamoDB locking (AWS), Terraform Cloud, GCS
- State contains sensitive data — encrypt at rest (S3 SSE), restrict access with IAM

**Common follow-ups:**
- "What happens if two people run terraform apply at the same time?" → state locking prevents this (DynamoDB `LockID` item)
- "How do you import existing resources?" → `terraform import`
- "What do you do if state is corrupted?" → restore from backup, `terraform state` subcommands

---

## Pattern 2: Module Structure

**They ask:** "How do you organize Terraform for multiple environments?"

**Pattern 1 — directory per environment:**
```
infra/
  environments/
    prod/
      main.tf       # calls modules
      terraform.tfvars
    staging/
      main.tf
      terraform.tfvars
  modules/
    vpc/
    ec2/
    rds/
```

**Pattern 2 — workspaces:**
- `terraform workspace new prod` → separate state per workspace
- Same code, different state files
- Simpler but less isolation; directory approach preferred for significant infra differences

**What they want to see:** you use modules to avoid duplication and separate state per environment.

---

## Pattern 3: State Manipulation

**They ask:** "How would you move a resource to a different module or rename it?"

```bash
terraform state mv module.old.aws_instance.app module.new.aws_instance.app
```

**Common use cases:**
- Refactoring module structure without destroying resources
- Renaming a resource block in code
- Moving a resource from unmodularized to modularized code

**They also ask about:**
- `terraform state rm` → remove resource from state without destroying it (orphan)
- `terraform state list` → see what's tracked

---

## Pattern 4: Plan vs Apply

**They ask:** "Walk me through your Terraform CI/CD workflow."

**Good answer:**
1. PR opened → `terraform fmt --check` and `terraform validate`
2. `terraform plan` runs in CI → output posted to PR as comment
3. Code review includes the plan (what will be created/destroyed/modified)
4. Merge to main → `terraform apply -auto-approve` (or manual approval gate)
5. State stored in S3, locks via DynamoDB

**What they watch for:**
- Running apply without reviewing plan first
- Not using remote state in teams
- No lock on concurrent runs

---

## Pattern 5: Dynamic Blocks and Meta-Arguments

**They ask:** "How do you avoid repeating yourself in Terraform?"

**`for_each` over a map:**
```hcl
resource "aws_security_group_rule" "ingress" {
  for_each = var.ingress_rules   # map of rule name → port
  type      = "ingress"
  from_port = each.value
  to_port   = each.value
  protocol  = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  security_group_id = aws_security_group.app.id
}
```

**Dynamic blocks:**
```hcl
resource "aws_security_group" "app" {
  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

**When to use which:**
- `for_each` on the resource → creates N separate resource instances (separate state entries)
- `dynamic` blocks → creates N inline blocks within ONE resource

---

## Pattern 6: Sensitive Values

**They ask:** "How do you handle secrets in Terraform?"

- Mark variables as `sensitive = true` → Terraform redacts them from plan output
- Never store secrets in `.tfvars` files committed to git
- Use `data "aws_secretsmanager_secret_version"` to pull secrets from Secrets Manager at apply time
- Use Vault provider for on-prem secrets
- SSM Parameter Store via `data "aws_ssm_parameter"`

**What they watch for:** secrets in state file are still plaintext — protect the state backend.

---

## Pattern 7: Common Errors

**"Error: resource already exists"**
→ Resource exists in cloud but not in state. Fix: `terraform import`.

**"Error acquiring state lock"**
→ Previous run crashed and left a lock. Fix: `terraform force-unlock <lock-id>` (verify no other run is active first).

**"Plan shows destroy on resource you didn't change"**
→ Usually means a dependency changed (like AMI ID), or the resource was manually modified outside Terraform (drift). Fix: `terraform refresh`, then review the plan carefully.

**"Module not found"**
→ Run `terraform init` after adding a new module or provider.
