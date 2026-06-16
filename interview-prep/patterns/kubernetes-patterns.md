# Kubernetes Interview Patterns

Common patterns from real DevOps/SRE interviews. Focus on what interviewers actually probe.

---

## Pattern 1: Debug a Pod That Won't Start

**They ask:** "A pod is in CrashLoopBackOff. Walk me through debugging it."

**The debugging sequence they want to see:**

```bash
kubectl get pod <name> -n <ns>          # current state
kubectl describe pod <name> -n <ns>     # Events section — tells you WHY
kubectl logs <name> -n <ns>             # app logs (may not exist if container never starts)
kubectl logs <name> -n <ns> --previous  # logs from previous crashed container
```

**Common causes and what they map to:**
- `CrashLoopBackOff` → container starts and exits; look at logs for exit reason
- `ImagePullBackOff` → can't pull image; check registry access, imagePullSecrets
- `OOMKilled` → memory limit too low; `kubectl describe pod` shows `OOMKilled` in Last State
- `Pending` → scheduling failure; describe pod → Events will show "Insufficient memory" or no nodes match
- `Init containers` → check `kubectl logs <pod> -c <init-container-name>`

---

## Pattern 2: Deployment Strategies

**They ask:** "How do you deploy a new version with zero downtime?"

**Three strategies:**

**Rolling update (default):**
- Gradually replaces pods; maxSurge and maxUnavailable control speed
- Zero downtime if readiness probes are set correctly
- Rollback: `kubectl rollout undo deployment/<name>`

**Blue-Green:**
- Two identical environments; switch traffic at Service/LB level
- Zero downtime, instant rollback (switch back)
- Costs double the resources during deploy

**Canary:**
- Send small % of traffic to new version
- Gradually increase if metrics look good
- Requires traffic splitting (Ingress controller with weights, or Istio)

**What they want to hear:** which strategy depends on risk tolerance, resource cost, and whether you need gradual validation.

---

## Pattern 3: StatefulSet vs Deployment

**They ask:** "When would you use a StatefulSet?"

**Deployment:**
- Stateless apps
- Pods are interchangeable
- Any pod can handle any request
- Example: web servers, API servers

**StatefulSet:**
- Requires stable network identity: pod name is predictable (`redis-0`, `redis-1`)
- Requires stable storage: PVC bound to specific pod persists across restarts
- Ordered startup/shutdown
- Example: Kafka, Redis, PostgreSQL, Elasticsearch

**Key difference:** StatefulSet pods have unique identities. Deployment pods don't.

---

## Pattern 4: RBAC

**They ask:** "A developer says they can't access pod logs in production. How do you fix it?"

**RBAC components:**
```
Role/ClusterRole    →  defines allowed verbs on resources
RoleBinding         →  binds a Role to a subject (user, group, ServiceAccount)
```

**Fix:**
```yaml
# Role that allows getting pods and reading logs
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
```

Then bind it to the developer's user or group with a RoleBinding.

**Debug command:** `kubectl auth can-i get pods/log --namespace production --as developer@company.com`

---

## Pattern 5: Resource Limits and OOMKilled

**They ask:** "What happens when a pod runs out of memory?"

- If memory exceeds `limits.memory` → kernel OOM killer terminates the container
- Pod status shows `OOMKilled` in Last State
- Container restarts (CrashLoopBackOff if it keeps happening)

**Fix:** increase memory limit, or find the memory leak in the app.

**What they want to see you distinguish:**
- `requests` = scheduler uses this to place the pod
- `limits` = enforced by cgroup; exceeding limit kills the container

No limit set = container can consume all node memory → dangerous in production.

---

## Pattern 6: Services and Ingress

**They ask:** "What's the difference between ClusterIP, NodePort, and LoadBalancer?"

| Type | Accessible from | Use case |
|---|---|---|
| ClusterIP | Inside cluster only | Service-to-service communication |
| NodePort | External via node IP + port | Dev/test, not production |
| LoadBalancer | External via cloud LB | Production traffic from internet |
| Ingress | External via HTTP rules | Route by hostname/path; one LB for many services |

**Production pattern:** LoadBalancer Service (or Ingress) → ClusterIP Services internally. Never expose NodePort in production.

---

## Pattern 7: Probes

**They ask:** "What's the difference between liveness and readiness probes?"

- **Readiness:** pod isn't ready to receive traffic yet (app still starting)
  → removed from Service endpoints until passing
- **Liveness:** pod is stuck/hung and needs to be restarted
  → triggers container restart when failing

**Golden rule:** always set readiness probes on your Deployments. Without them, traffic goes to pods that haven't finished initializing.

---

## EKS-Specific Patterns

**IRSA (IAM Roles for Service Accounts):**
- Annotate a ServiceAccount with an IAM role ARN
- EKS uses OIDC to issue short-lived tokens
- Pod gets AWS credentials scoped to the role, no access keys needed

**Managed node groups vs Fargate:**
- Node groups: you manage EC2 nodes (more control, supports DaemonSets)
- Fargate: serverless; AWS provisions and manages underlying infra
- Fargate limitation: no DaemonSets, no privileged containers
