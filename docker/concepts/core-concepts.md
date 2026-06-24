# Docker Core Concepts

> Docker is named after shipping containers — the metal boxes that standardized global freight. Before them, every shipment was custom-packed. After them: standard box, any crane, any ship, any port. Docker does the same for software: standard container, any machine, any cloud, any environment.

---

## The problem Docker solves

"It works on my machine" — the classic. Your app runs on your laptop but fails in production because production has a different OS, different Python version, different library, different config.

Docker solves this by packaging **the app + everything it needs** into one portable unit. You ship the whole environment — not just the code. The container runs exactly the same on your laptop, in CI, and in production.

---

## Containers vs Virtual Machines

Both isolate applications. The difference is what they share:

```
Virtual Machine                      Container

┌─────────────────────┐              ┌─────────────────────┐
│  Your App           │              │  Your App           │
│  App dependencies   │              │  App dependencies   │
│  Full OS (2-4GB)    │              │  (no full OS)       │
│─────────────────────│              │─────────────────────│
│  Hypervisor         │              │  Docker Engine      │
│─────────────────────│              │─────────────────────│
│  Host OS            │              │  Host OS (kernel)   │
└─────────────────────┘              └─────────────────────┘

Startup: 30-60 seconds               Startup: milliseconds
Size: GBs                            Size: MBs
Isolation: full OS boundary          Isolation: kernel namespaces
```

**Apartment analogy:**
- VM = renting an entire apartment (your own kitchen, bathroom, electrical system — fully separate)
- Container = renting a room in a shared building (your own private space, but shared plumbing, shared roof, same landlord)

VMs are heavier but offer stronger isolation. Containers share the host kernel — faster and lighter, but a kernel vulnerability affects all containers on that host.

**In practice:** containers for apps (the standard today), VMs for the host machines that containers run on. In AWS: EC2 is the VM, Docker containers run inside that EC2.

---

## Images vs Containers

The distinction that confuses most beginners:

```
Image                                Container
─────────────────────────────────────────────────────────
Recipe / blueprint                   The cooked meal
Class definition in OOP              Instance (object) of that class
Snapshot stored on disk              Running process in memory
Read-only                            Has a thin writable layer on top
Built once                           Created and destroyed constantly
One image → many containers          Each container is independent
```

A Python class is defined once. You create many objects from it — each independent, but sharing the class definition. Same here: build the image once, run it as 1 or 1,000 containers. Stopping or deleting a container never affects the image.

```bash
docker images                        # list images stored on this machine
docker ps                            # list running containers
docker ps -a                         # all containers (running + stopped)
```

---

## Layers — why Docker images are efficient

Every instruction in a Dockerfile creates a **layer**. Think of it like Git commits: each layer is a diff on top of the previous one. Layers are cached and shared across images.

```
Dockerfile instruction:              Resulting layer:

FROM ubuntu:22.04           →        [ubuntu base]          shared by all ubuntu images on this host
RUN apt-get install python  →        [python install]       cached after first build
COPY app.py /app/           →        [your code]            changes most often
CMD ["python", "/app/app.py"] →      [metadata only, no size]
```

**Why layers matter:**
- **Build cache:** change `app.py` → Docker reuses the cached python install layer, only rebuilds from COPY onward. Fast builds.
- **Storage efficiency:** two images that both use `ubuntu:22.04` share that base layer on disk — not two copies.
- **Pull efficiency:** `docker pull` only downloads layers you don't already have locally.

**The golden rule:** put things that change least at the TOP of the Dockerfile, things that change most at the BOTTOM. Your base OS rarely changes; your app code changes every commit.

---

## The core workflow

```bash
# 1. Write a Dockerfile (see dockerfile.md)

# 2. Build an image from it
docker build -t myapp:1.0 .          # -t = tag (name:version), . = build context directory

# 3. Run a container from the image
docker run myapp:1.0                  # foreground — you see logs
docker run -d myapp:1.0              # -d = detached (background)
docker run -p 8080:3000 myapp:1.0    # -p = port mapping host:container
docker run --name web myapp:1.0      # give the container a name

# 4. Inspect what's running
docker ps                             # running containers
docker logs web                       # stdout/stderr of container "web"
docker logs -f web                    # live tail (like tail -f)
docker exec -it web bash              # open a shell inside the running container

# 5. Stop and clean up
docker stop web                       # graceful (sends SIGTERM, waits for exit)
docker kill web                       # immediate (SIGKILL)
docker rm web                         # delete a stopped container
docker rmi myapp:1.0                 # delete an image
```

---

## Registries — where images live

A registry is a server that stores and serves Docker images. Think of it like GitHub, but for images instead of code.

```
Docker Hub (hub.docker.com)    ← public default; where official images live (nginx, postgres, python...)
Amazon ECR                     ← AWS private registry, what you use in production
GitHub Container Registry      ← ghcr.io, integrated with GitHub repos
Self-hosted                    ← Harbor, GitLab Container Registry
```

```bash
# Push to Docker Hub
docker tag myapp:1.0 dorbitton/myapp:1.0
docker push dorbitton/myapp:1.0

# Pull a public image
docker pull nginx:latest

# AWS ECR workflow
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag myapp:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

---

## → How this maps to K8s and AWS

**K8s:** the image is the same artifact. K8s pulls your image from a registry (ECR, Docker Hub, GCR) and runs it in a Pod. The Dockerfile you write locally is the exact same image K8s uses — nothing changes at the image level.

**AWS ECR:** ECR is Docker Hub but private and inside your AWS account. Both ECS and EKS pull from ECR. IAM roles control access — no passwords needed in prod.

**ECS vs EKS vs Fargate:**
```
ECS (Elastic Container Service)    ← AWS-native orchestration, simpler, less overhead
EKS (Elastic Kubernetes Service)   ← managed Kubernetes, more powerful / more complex
Fargate                            ← serverless containers: no EC2 nodes to manage
```

For senior SRE interviews: ECS uses "task definitions" (equivalent to docker run flags), EKS uses K8s manifests (Deployments, Services), ECR is the image store for both.

**Interview question:** "What's the difference between a Docker image and a container?"
→ Image is the read-only blueprint. Container is the running instance. Many containers can run from one image. Deleting a container doesn't affect the image.

**Interview question:** "How are containers different from VMs?"
→ Containers share the host kernel (fast, lightweight), VMs include a full OS (heavier but stronger isolation). In production, containers run on top of VMs — containers for apps, VMs for the hosts.
