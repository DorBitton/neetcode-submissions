# Docker Core Concepts

> The mental model. Read this before doing any scenarios.

---

## The problem Docker solves

"It works on my machine" — the classic. Your app runs on your laptop but fails in production because production has a different OS, different Python version, different library, different config.

Docker solves this by packaging **the app + everything it needs** into one portable unit.

---

## Containers vs Virtual Machines

Both isolate applications. The difference is what they share:

```
Virtual Machine:                    Container:

┌─────────────────────┐             ┌─────────────────────┐
│  Your App           │             │  Your App           │
│  App dependencies   │             │  App dependencies   │
│  Full OS (2-4GB)    │             │  (no OS — shared)   │
│─────────────────────│             │─────────────────────│
│  Hypervisor         │             │  Docker Engine      │
│─────────────────────│             │─────────────────────│
│  Host OS            │             │  Host OS (kernel)   │
└─────────────────────┘             └─────────────────────┘

Startup: 30-60 seconds              Startup: milliseconds
Size: GBs                           Size: MBs
Isolation: full OS boundary         Isolation: kernel namespaces
```

**VMs are heavier but stronger isolation.** Containers share the host kernel — faster and lighter, but if the kernel has a vulnerability, all containers are exposed.

**In practice:** containers for apps (the standard now), VMs for infrastructure (the host machines containers run on). In AWS: EC2 is the VM, Docker containers run on top of EC2.

---

## Images vs Containers

The distinction that confuses most beginners:

```
Image                               Container
─────────────────────────────────────────────────────────
Blueprint / template                Running instance
Read-only                           Has a writable layer on top
Like a class in OOP                 Like an object (instance)
Stored on disk / in a registry      Running in memory
One image → many containers         Each container is independent
```

```bash
docker images                       # list images on this machine
docker ps                           # list running containers
docker ps -a                        # list all containers (including stopped)
```

---

## Layers — why Docker images are efficient

Every instruction in a Dockerfile creates a **layer**. Layers are cached and shared.

```
Dockerfile:                         Resulting layers (bottom to top):

FROM ubuntu:22.04            →      [ubuntu:22.04 base]         ← shared by all ubuntu images
RUN apt-get install python   →      [python installation]        ← cached after first build
COPY app.py /app/            →      [your app code]             ← changes most often
CMD ["python", "/app/app.py"] →     [metadata]
```

**Why layers matter:**
- **Build cache:** if line 3 doesn't change, Docker reuses the cached layer. Builds are fast.
- **Storage efficiency:** two images that both use `ubuntu:22.04` share that layer on disk — not two copies.
- **Pull efficiency:** pulling an image only downloads layers you don't already have.

**The golden rule:** put things that change least at the top of the Dockerfile, things that change most at the bottom. Your app code changes constantly; your base OS doesn't.

---

## The core workflow

```bash
# 1. Write a Dockerfile
# 2. Build an image from it
docker build -t myapp:1.0 .         # -t = tag (name:version), . = Dockerfile location

# 3. Run a container from the image
docker run myapp:1.0                # run it
docker run -d myapp:1.0            # -d = detached (background)
docker run -p 8080:80 myapp:1.0    # -p = port mapping (host:container)
docker run --name web myapp:1.0    # give it a name

# 4. Inspect what's running
docker ps                           # running containers
docker logs web                     # stdout/stderr of container "web"
docker logs -f web                  # follow (live tail)
docker exec -it web bash           # get a shell inside a running container

# 5. Stop and clean up
docker stop web                     # graceful stop (SIGTERM, waits)
docker kill web                     # immediate stop (SIGKILL)
docker rm web                       # delete stopped container
docker rmi myapp:1.0               # delete image
```

---

## Registries — where images live

```
Docker Hub (hub.docker.com)    ← public default registry
Amazon ECR                     ← AWS private registry (used in prod)
GitHub Container Registry      ← ghcr.io
Self-hosted                    ← Harbor, GitLab registry
```

```bash
# Push to Docker Hub
docker tag myapp:1.0 dorbitton/myapp:1.0
docker push dorbitton/myapp:1.0

# Pull from Docker Hub
docker pull nginx:latest

# AWS ECR workflow
aws ecr get-login-password | docker login --username AWS --password-stdin <ecr-url>
docker tag myapp:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

---

## → How this maps to K8s and AWS

**K8s:** the image is the exact same artifact. K8s pulls your image from a registry (ECR, Docker Hub, GCR) and runs it in a Pod. The Dockerfile you write for Docker is the same one K8s uses. Nothing changes at the image level.

**AWS ECR:** ECR is Docker Hub but private and inside AWS. When you run containers in ECS or EKS, they pull from ECR. IAM roles control which services can pull which images — no passwords needed.

**ECS vs EKS:**
```
ECS (Elastic Container Service)    ← AWS-native orchestration, simpler
EKS (Elastic Kubernetes Service)   ← managed Kubernetes, more powerful/complex
Fargate                            ← serverless: run containers without managing EC2
```

For senior SRE interviews: know that ECS uses "task definitions" (similar to docker run flags), EKS uses K8s manifests. ECR is where images live in AWS regardless of which one you use.
