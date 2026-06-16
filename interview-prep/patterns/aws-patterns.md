# AWS Interview Patterns

Common patterns from real DevOps/SRE interviews. Not a tutorial — these are the angles interviewers come at AWS from.

---

## Pattern 1: VPC Design Questions

**They ask:** "Walk me through how you'd design a VPC for a production application."

**What they want to hear:**
- Public vs private subnet split (web tier public, app/DB private)
- NAT Gateway for outbound-only internet from private subnets
- Security groups (stateful, instance-level) vs NACLs (stateless, subnet-level)
- Separate VPCs per environment (prod/staging/dev) + Transit Gateway or peering

**Red flags they watch for:**
- Putting databases in public subnets
- Using NACLs for everything (they're stateless — most people want SGs)
- Not mentioning least-privilege security groups

**Your answer structure:**
1. Start with the separation: public subnets for load balancers, private for app, private for DB
2. Cover internet access: IGW for public, NAT GW for private outbound
3. Cover connectivity: how do multiple VPCs connect? (TGW at scale, peering for few)
4. Cover security: layered — SG > NACL > WAF if they want

---

## Pattern 2: IAM Role vs User

**They ask:** "When would you use an IAM role vs an IAM user?"

**What they want to hear:**
- Users = humans with long-term credentials (avoid for services)
- Roles = assumed by services, Lambda, EC2, EKS pods (short-lived tokens)
- IRSA = IAM Roles for Service Accounts in EKS (pods don't need access keys)
- Never embed access keys in code or containers

**Follow-up they often add:** "How does a pod in EKS access S3?"
- IRSA: annotate ServiceAccount → OIDC provider → IAM role trust policy
- Pod gets short-lived STS token, no access keys needed

---

## Pattern 3: How Would You Debug X

**They ask:** "Users report the app is slow. How do you debug it?"

**AWS angle — what they want to see you reach for:**
- CloudWatch metrics: EC2 CPU/mem, ALB target response time, RDS latency
- CloudWatch Logs Insights: query log groups for errors, slow queries
- X-Ray: distributed trace to find which service is the bottleneck
- ALB access logs: look at `target_processing_time` field
- Check SGs/NACLs if there are timeouts (connectivity vs latency)

**Structure:** Observe → Isolate → Hypothesize → Test → Fix

---

## Pattern 4: High Availability Architecture

**They ask:** "How would you make this application highly available?"

**Must-haves to mention:**
- Multi-AZ: spread across at least 2 availability zones
- ALB with health checks routing away from unhealthy targets
- Auto Scaling Groups: replace failed instances automatically
- RDS Multi-AZ: synchronous replica in another AZ for automatic failover
- Route53 health checks: failover at DNS level across regions

**Advanced:** Active-active vs active-passive per region, RTO/RPO, error budget

---

## Pattern 5: Cost Optimization

**They ask:** "How would you reduce AWS costs?"

**Common levers:**
- Right-sizing: use Compute Optimizer recommendations, don't over-provision
- Reserved Instances or Savings Plans for predictable workloads
- Spot Instances for stateless, fault-tolerant workloads (CI runners, batch)
- S3 lifecycle policies: move to Infrequent Access → Glacier over time
- Identify and terminate unused resources (Trusted Advisor, Cost Explorer)
- Nat Gateway cost: reduce cross-AZ data transfer, consider VPC endpoints for S3/DynamoDB

---

## Pattern 6: Security Questions

**They ask:** "How do you prevent EC2 instances from accessing the internet?"

- Put them in private subnets (no IGW route)
- Remove NAT Gateway if no outbound needed
- Use VPC endpoints for AWS services (no data leaves VPC)
- SG: allow only specific inbound from ALB SG, no 0.0.0.0/0

**They ask:** "How do you rotate secrets?"

- AWS Secrets Manager: automatic rotation for RDS passwords, API keys
- Never hardcode in env vars in source code
- Reference secrets by ARN in ECS task def or K8s via External Secrets Operator

---

## Key Numbers to Know

| Thing | Number |
|---|---|
| AZs per region | typically 3 (some have 2 or 6) |
| S3 durability | 11 nines (99.999999999%) |
| EC2 default SG | no inbound allowed |
| RDS Multi-AZ RPO | ~1 second (synchronous replication) |
| Route53 health check interval | 30s (or 10s fast) |
