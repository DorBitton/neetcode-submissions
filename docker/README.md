# Docker

> Containers package your app and its dependencies into one portable unit. Learn this once — K8s and AWS ECS/EKS build directly on top of it.

---

## Why Docker clicks with K8s and AWS

Docker is the **building block**. Once you understand it, K8s and AWS are just "how do we run many of these at scale":

```
Docker                    Kubernetes                AWS
──────────────────────────────────────────────────────────────────
Image                  →  Same image, pulled from ECR
Container              →  Pod (1+ containers)        ECS Task
docker run             →  Deployment                 ECS Service
-p 8080:80             →  Service (ClusterIP/NodePort/LB)
ENV in Dockerfile      →  ConfigMap / Secret
Volume                 →  PersistentVolume (PV+PVC)
Bind mount             →  hostPath / emptyDir
Bridge network         →  Pod network (CNI)
Overlay network        →  Cluster network
docker-compose         →  Helm chart / K8s manifests
Docker Hub             →                             Amazon ECR
docker run (1 host)    →                             ECS Fargate (serverless)
```

**The pattern:** every Docker concept has a direct K8s/AWS equivalent. Learn Docker deeply and K8s is mostly "Docker, but distributed."

---

## KillerCoda Scenarios

**Workflow:** read `concepts/core-concepts.md` first (30 min). Then do scenarios grouped below — read the notes file after each group while it's fresh.

### Group 1 — Images and Dockerfiles (do these first)
| Scenario | Status | Notes file |
|---|---|---|
| Building an image | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |
| CMD or ENTRYPOINT | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |
| ADD or COPY | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |
| Dockerfile best practices | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |
| Updating containerized application | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |

### Group 2 — Networking
| Scenario | Status | Notes file |
|---|---|---|
| Port-forwarding in Docker | ⬜ | [`concepts/networking.md`](./concepts/networking.md) |
| Network drivers | ⬜ | [`concepts/networking.md`](./concepts/networking.md) |

### Group 3 — Storage and Config
| Scenario | Status | Notes file |
|---|---|---|
| Using volume mounts | ⬜ | [`concepts/volumes.md`](./concepts/volumes.md) |
| Using bind mounts | ⬜ | [`concepts/volumes.md`](./concepts/volumes.md) |
| Using environment variables | ⬜ | [`concepts/dockerfile.md`](./concepts/dockerfile.md) |

---

## File Map

| File | What's in it | Status |
|---|---|---|
| `CHEATSHEET.md` | All docker commands on one page | ⬜ |
| `concepts/core-concepts.md` | Mental model — containers vs VMs, images vs containers, layers | ✅ |
| `concepts/dockerfile.md` | Dockerfile instructions, COPY vs ADD, CMD vs ENTRYPOINT, best practices, ENV | ✅ |
| `concepts/networking.md` | Bridge/host/overlay drivers, port forwarding, container DNS | ✅ |
| `concepts/volumes.md` | Bind mounts vs volumes, persistence, the K8s mapping | ✅ |
| `concepts/compose.md` | docker-compose, multi-service setups | ⬜ |
| `interview-questions.md` | 20 Docker questions | ⬜ |

---

## Resources
- KillerCoda Docker scenarios (what you're doing now)
- [docs.docker.com](https://docs.docker.com) — reference for any command
- [hub.docker.com](https://hub.docker.com) — public image registry

---

## Study order

```
1. Read concepts/core-concepts.md              ← do this before any scenarios
2. KillerCoda Group 1 (Dockerfiles)            ← building + CMD/ENTRYPOINT + COPY + best practices
3. Read concepts/dockerfile.md                 ← reinforces the 5 Dockerfile scenarios
4. KillerCoda Group 2 (Networking)             ← port forwarding + network drivers
5. Read concepts/networking.md
6. KillerCoda Group 3 (Storage + Config)       ← volumes + bind mounts + env vars
7. Read concepts/volumes.md
8. Answer docker/interview-questions.md out loud
```
