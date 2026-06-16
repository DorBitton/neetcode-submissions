# CI/CD

Continuous Integration and Continuous Delivery pipelines. Covers GitHub Actions, Jenkins, and GitOps with ArgoCD.

---

## Planned Topics

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | GitHub Actions syntax quick ref, common patterns | ⬜ |
| `concepts/pipelines.md` | Pipeline stages: build → test → scan → deploy | ⬜ |
| `concepts/github-actions.md` | Workflows, jobs, steps, secrets, matrix builds | ⬜ |
| `concepts/jenkins.md` | Jenkinsfile, stages, shared libraries, agents | ⬜ |
| `concepts/gitops-argocd.md` | GitOps model, ArgoCD sync, App of Apps pattern | ⬜ |
| `concepts/security-scanning.md` | SonarQube, OWASP ZAP, Aqua Security, Terrascan, Secrets Manager | ⬜ |
| `interview-questions.md` | 20 CI/CD questions | ⬜ |

---

## Practice Tasks (prepare.sh)

Work through these at [prepare.sh/track/devops](https://prepare.sh/track/devops) → CI/CD section.

### Medium (5)
- [ ] Docker Image Tagging with Commit SHA
- [ ] Matrix Build Strategy
- [ ] Multi-Job Workflow with Artifact Handoff
- [ ] Path-Based Workflow Execution
- [ ] Automated Rollback on Deployment Failure

---

## Cross-references
- `kubernetes/` → GitOps deploys to K8s; ArgoCD manages K8s resources
- `docker/` → CI builds Docker images; CD deploys them
- `terraform/` → Terraform can be run in CI for infra changes
