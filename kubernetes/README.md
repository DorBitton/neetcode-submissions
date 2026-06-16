# Kubernetes

Container orchestration. On-prem K8s and EKS (AWS managed).

---

## Planned Topics

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | kubectl commands on one page | ⬜ |
| `concepts/pods-and-deployments.md` | Pods, ReplicaSets, Deployments, rolling updates | ⬜ |
| `concepts/services-and-ingress.md` | ClusterIP, NodePort, LoadBalancer, Ingress | ⬜ |
| `concepts/storage.md` | PV, PVC, StorageClass | ⬜ |
| `concepts/rbac.md` | Roles, ClusterRoles, ServiceAccounts | ⬜ |
| `concepts/networking.md` | CNI, pod networking, network policies | ⬜ |
| `concepts/eks.md` | What EKS adds — managed control plane, node groups, Fargate, IRSA | ⬜ |
| `interview-questions.md` | 20 Kubernetes questions | ⬜ |

---

## Practice Tasks (prepare.sh)

Work through these at [prepare.sh/track/devops](https://prepare.sh/track/devops) → Kubernetes section.

### Easy (4)
- [ ] Dynamic Volume Expansion
- [ ] Create Namespace
- [ ] Pod with Readiness Probe
- [ ] Pod Viewer Access

### Medium (10)
- [ ] Crashing Misconfigured Pod
- [ ] Image Pull BackOff and Secrets
- [ ] CronJob Schedule Misconfiguration
- [ ] Traffic Splitting with Native Kubernetes
- [ ] ConfigMap Reload with Sidecar
- [ ] Implement StatefulSet with Stable DNS
- [ ] StorageClass and PVC Expansion
- [ ] OOMKilled Pod Analysis & Fix
- [ ] Secure Internal Service Communication
- [ ] Custom Resource Definition Setup

### Hard (1)
- [ ] CRD Schema Validation

---

## Cross-references
- `aws/` → `aws/concepts/eks.md` for the AWS-specific angle
- `networking/` → K8s networking builds on L3/L4 concepts

---

## Resources
- KillerCoda has extensive K8s scenarios
- killer.sh for CKA exam prep (good even if not taking the exam)
