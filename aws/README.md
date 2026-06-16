# AWS

Core services for SRE. Mapped to on-prem equivalents throughout.

---

## Planned Topics

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | AWS CLI commands + key services | ⬜ |
| `concepts/networking/vpc.md` | VPC, subnets, route tables, IGW, NAT | ⬜ |
| `concepts/networking/security-groups.md` | SGs vs NACLs, rules, patterns | ⬜ |
| `concepts/networking/route53.md` | DNS, routing policies, health checks | ⬜ |
| `concepts/compute/ec2.md` | Instance types, AMIs, user data, placement | ⬜ |
| `concepts/compute/ecs.md` | Containers on AWS without K8s | ⬜ |
| `concepts/load-balancers.md` | ALB vs NLB vs CLB — maps to networking/ | ⬜ |
| `concepts/eks.md` | EKS — maps to kubernetes/ | ⬜ |
| `concepts/storage/s3.md` | Buckets, policies, lifecycle, versioning | ⬜ |
| `concepts/storage/ebs-efs.md` | Block vs file storage | ⬜ |
| `concepts/iam.md` | Users, roles, policies, IRSA, least privilege | ⬜ |
| `interview-questions.md` | 25 AWS questions | ⬜ |

---

## Practice Tasks (prepare.sh)

Work through these at [prepare.sh/track/devops](https://prepare.sh/track/devops) → AWS section.

### Easy (7)
- [ ] Create AWS IAM Admin User with Group and Policy
- [ ] Create IAM Role for EC2 with Full IAM Access
- [ ] Create a Hello World Lambda Function
- [ ] Launch an EC2 Web Server Instance
- [ ] Audit and Enforce Least-Privilege IAM Permissions
- [ ] Create Route 53 Hosted Zone and DNS Records
- [ ] Create Route 53 Health Checks

### Medium (1)
- [ ] Design Egress Only VPC with NAT

### Hard (2)
- [ ] Build a Serverless API with Lambda, API Gateway, and DynamoDB
- [ ] Deploy an Internal Web App with VPC, EC2, ALB, and Route 53

---

## Cross-references
- Load balancers → see `networking/` for theory and F5 comparison
- EKS → see `kubernetes/` for K8s concepts
- Terraform → see `terraform/` for deploying AWS infra as code
