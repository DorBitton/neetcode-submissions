# Dockerfiles — Building Images

> A Dockerfile is a recipe. Each line is one step. The final image is the printed recipe card. A running container is the dish you cooked from it.

---

## What is a Dockerfile?

When you run `docker build`, Docker reads a file called `Dockerfile` (no extension) line by line and executes each instruction. Each instruction creates a **layer** stacked on top of the previous one.

```
Dockerfile line 1: FROM node:20-alpine   → [base layer: Node.js + Alpine Linux]
Dockerfile line 2: WORKDIR /app          → [layer: set working directory]
Dockerfile line 3: COPY package*.json ./ → [layer: dependency manifest]
Dockerfile line 4: RUN npm ci            → [layer: node_modules installed]
Dockerfile line 5: COPY . .              → [layer: your app code]
Dockerfile line 6: CMD ["node", "app.js"]→ [metadata]
                                           ──────────────────────
                                           Final image = all layers stacked
```

The image is **read-only**. When you `docker run` it, Docker adds a thin writable layer on top. Stop and remove the container — that writable layer is gone. The image remains unchanged.

---

## The essential instructions

Here's a full Dockerfile with every instruction you'll use 90% of the time:

```dockerfile
# Always the first line: which base image to start from
FROM node:20-alpine

# Working directory inside the container — all paths below are relative to this
WORKDIR /app

# Copy dependency manifest BEFORE source code (cache trick — explained later)
COPY package*.json ./

# Install dependencies (runs during build, not at runtime)
RUN npm ci --only=production

# Now copy the rest of the app
COPY . .

# Environment variables baked into the image (can be overridden at runtime)
ENV NODE_ENV=production
ENV PORT=3000

# Documents which port this app listens on (metadata only — doesn't open it)
EXPOSE 3000

# What to run when the container starts
CMD ["node", "server.js"]
```

### Each instruction explained

**`FROM`** — Every Dockerfile starts here. You pick a base image — a pre-built starting point. You never start from a blank OS unless you're doing advanced things.

```dockerfile
FROM node:20-alpine        # Node.js 20 on Alpine Linux (~40MB)
FROM python:3.11-slim      # Python 3.11 on Debian Slim (~100MB)
FROM golang:1.20-alpine    # Go compiler on Alpine (for building Go apps)
FROM ubuntu:22.04          # Full Ubuntu (~80MB) — usually overkill
```

The name before the `:` is the image name, after is the tag (version). `latest` is the default if you omit the tag — avoid it in production, it changes without warning.

**`WORKDIR`** — Sets the working directory inside the container for all subsequent instructions. Think of it as `mkdir -p /app && cd /app` that persists for the whole Dockerfile.

```dockerfile
WORKDIR /app    # creates /app if it doesn't exist, sets it as current dir
```

**`COPY`** — Copies files from your host machine into the image. First arg is the source (on your machine), second is the destination (in the image).

```dockerfile
COPY package.json ./          # copy one file into WORKDIR
COPY src/ /app/src/           # copy a whole directory
COPY . .                      # copy everything here → into WORKDIR
COPY package*.json ./         # globs work
```

**`RUN`** — Executes a shell command during build time. This is how you install packages, compile code, create directories. Each `RUN` creates a new layer.

```dockerfile
RUN npm install
RUN apt-get update && apt-get install -y curl
RUN go build -o /bin/server ./cmd/server
```

**`EXPOSE`** — Documents which port the app listens on. It is **metadata only** — it does not actually open the port. You open ports with `-p` at runtime.

```dockerfile
EXPOSE 3000    # tells readers: this container listens on 3000
               # to actually publish it: docker run -p 8080:3000 myapp
```

**`CMD`** — The default command when the container starts. Can be overridden at runtime. Explained in detail in the next section.

```dockerfile
CMD ["node", "server.js"]    # container starts → runs: node server.js
```

---

## COPY vs ADD

Both copy files into the image. **Always use COPY. ADD has hidden magic.**

| | `COPY` | `ADD` |
|---|---|---|
| Copy local files | ✅ | ✅ |
| Fetch from a URL | ❌ | ✅ (downloads it) |
| Auto-extract tar archives | ❌ | ✅ (extracts automatically) |
| Predictable | ✅ | ⚠️ the auto-extract surprises people |

```dockerfile
COPY app.py /app/          # explicit: copies the file as-is
COPY src/ /app/src/

ADD archive.tar.gz /app/   # auto-extracts: contents appear as /app/file1, /app/file2...
                           # most people find this surprising
```

**Rule:** use `COPY` for everything. Use `ADD` only if you specifically need the auto-extract feature — which is rare.

---

## CMD vs ENTRYPOINT

The most common Dockerfile interview question. Both define what runs when a container starts. The difference is how they handle runtime arguments.

### CMD — the default command (replaceable)

```dockerfile
CMD ["node", "server.js"]
```

```bash
docker run myapp                     # runs: node server.js      (the CMD)
docker run myapp node --version      # CMD replaced: runs: node --version
docker run myapp bash                # CMD replaced: runs: bash
```

CMD is **completely replaced** when you pass arguments to `docker run`. Use it for a sensible default that might be overridden.

### ENTRYPOINT — the fixed executable (appended to, not replaced)

```dockerfile
ENTRYPOINT ["node"]
```

```bash
docker run myapp                     # runs: node          (needs an argument)
docker run myapp server.js           # runs: node server.js (argument appended)
docker run myapp --version           # runs: node --version (argument appended)
```

Arguments to `docker run` are **appended** to ENTRYPOINT — the container always runs `node`.

### ENTRYPOINT + CMD together — the standard pattern

```dockerfile
ENTRYPOINT ["node"]       # the container IS a node runner
CMD ["server.js"]         # by default, run server.js
```

```bash
docker run myapp                        # node server.js    (ENTRYPOINT + CMD combined)
docker run myapp other.js               # node other.js     (CMD replaced by argument)
docker run --entrypoint python myapp    # python            (override ENTRYPOINT itself)
```

**Mental model:**
```
ENTRYPOINT = what the container IS   (the program — not easily changed)
CMD        = the default input       (what it processes by default — easily overridden)
```

**When to use which:**
```
CMD only          → flexible image where the exact command varies
ENTRYPOINT only   → container wraps exactly one tool (a CLI binary)
ENTRYPOINT + CMD  → fixed program, overridable defaults — the most common pattern
```

### Shell form vs Exec form — why the square brackets matter

```dockerfile
# Shell form — avoid for CMD/ENTRYPOINT
CMD node server.js            # Docker actually runs: /bin/sh -c "node server.js"

# Exec form — use this
CMD ["node", "server.js"]     # Docker runs: node server.js   directly
```

**Why exec form matters:** with shell form, `docker stop` sends SIGTERM to `/bin/sh`, not to `node`. Your app never receives the shutdown signal and gets killed hard (SIGKILL) after the timeout. Exec form sends signals directly to your process — it can shut down gracefully.

---

## Environment Variables — ENV and ARG

### ENV — runtime variables (live in the image)

```dockerfile
ENV NODE_ENV=production
ENV DB_HOST=localhost
ENV DB_PORT=5432
```

Available during build AND in the running container.

```bash
docker run -e NODE_ENV=staging myapp       # override one variable
docker run --env-file .env myapp           # override from a file
docker inspect myapp | grep -A5 Env        # see what's baked in
```

### ARG — build-time only (gone when build finishes)

```dockerfile
ARG APP_VERSION=1.0
RUN echo "Building version $APP_VERSION"   # available here during build
# APP_VERSION is NOT available in the running container
```

```bash
docker build --build-arg APP_VERSION=2.0 .
```

ARG is for build-time configuration: version numbers, build flags, which registry to pull from.

**Security:** never put secrets in ARG — they appear in `docker history`. Use runtime secrets management (K8s Secrets, AWS Secrets Manager) instead.

---

## Layer caching — the most important build optimization

Every Dockerfile instruction creates a layer. Docker caches each layer and reuses it on the next build — **unless something above it changed**. A cache miss invalidates all layers below it too.

### The problem

```dockerfile
FROM golang:1.20-alpine
WORKDIR /src
COPY . .              # copies ALL source files, including main.go
RUN go mod download   # downloads all dependencies (30-60 seconds)
RUN go build -o /bin/server ./cmd/server
```

You change one comment in `main.go` and rebuild:

```
FROM golang:1.20-alpine    ✅ cache hit
WORKDIR /src               ✅ cache hit
COPY . .                   ❌ cache miss — main.go changed
RUN go mod download        ❌ must re-run   ← 60 seconds wasted every time
RUN go build               ❌ must re-run
```

`go mod download` re-runs on every single commit, even when `go.mod` never changed.

### The fix — copy slow-changing files before fast-changing ones

```dockerfile
FROM golang:1.20-alpine
WORKDIR /src
COPY go.mod go.sum ./   # copy only the dependency manifest (rarely changes)
RUN go mod download     # NOW this is cached until go.mod actually changes
COPY . .                # source code (changes often — that's expected)
RUN go build -o /bin/server ./cmd/server
```

Same `main.go` change now:

```
FROM golang:1.20-alpine    ✅ cache hit
WORKDIR /src               ✅ cache hit
COPY go.mod go.sum ./      ✅ cache hit — go.mod didn't change
RUN go mod download        ✅ cache hit — SKIPPED (60 seconds saved)
COPY . .                   ❌ cache miss — expected, code changed
RUN go build               ❌ must re-run — expected
```

### The pyramid — what belongs where

```
CHANGES LEAST → top of Dockerfile (cache stays warm)
────────────────────────────────────────────────────
FROM base image
OS-level packages (apt-get, apk)
Language runtime configuration
Dependency manifest (go.mod, package.json, requirements.txt, pom.xml)
Dependencies installed (go mod download, npm ci, pip install, mvn)
────────────────────────────────────────────────────
CHANGES MOST → bottom of Dockerfile
Your source code (COPY . .)
Build output (go build, npm run build, tsc)
```

### The same pattern in every language

```dockerfile
# Node.js
COPY package*.json ./
RUN npm ci
COPY . .

# Python
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Go
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# Java (Maven)
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src

# Ruby
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
```

**Interview answer for "how do you reduce CI build times?":** layer cache ordering — copy dependency manifests before source code so dependency installation is cached across code changes.

---

## Dockerfile best practices

### 1. Use a minimal base image

```dockerfile
# ❌ Heavy — ~80MB of OS overhead, large attack surface
FROM ubuntu:22.04

# ✅ Minimal
FROM python:3.11-alpine     # Alpine Linux + Python
FROM python:3.11-slim       # Slim Debian — better glibc compatibility
FROM node:20-alpine
```

Smaller base = smaller image = faster registry pulls = smaller attack surface.

### 2. Combine RUN commands to reduce layers

```dockerfile
# ❌ Three separate layers — apt cache persists in layer 1 forever
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ One layer — cleanup is in the same layer that created the cache
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

If you clean up in a separate RUN, the garbage is still in the prior layer — it's baked into the image.

### 3. Multi-stage builds — don't ship your build tools

**The problem:** compiling Go, Java, TypeScript, Rust requires a compiler, build tools, and source code. None of that should exist in a production image.

**The factory analogy:** a car factory has enormous machinery. When the car is done, you ship the car — not the factory. Multi-stage builds let you compile in a "factory" stage and ship only the output.

```dockerfile
# Stage 1: the factory (big — has the Go compiler)
FROM golang:1.20-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/server ./cmd/server

# Stage 2: the product (tiny — has only the compiled binary)
FROM scratch
COPY --from=builder /bin/server /bin/server
ENTRYPOINT ["/bin/server"]
```

`COPY --from=builder /bin/server /bin/server` pulls the compiled binary out of the builder stage. The final image contains **only what you explicitly COPY into it** — no compiler, no source code, no Go runtime, no shell.

**`FROM scratch` — the zero-byte starting point:**

`scratch` is a special Docker keyword meaning "start from an empty filesystem." Literally 0 bytes.

```
Stage 1 (builder):   ~300MB — Go compiler + Alpine + source code + binary
Final image:          ~10MB — just the compiled binary

30x smaller.
```

This works because a Go binary compiled with `CGO_ENABLED=0` is **statically linked** — it contains everything it needs and runs directly on the Linux kernel without needing libc, glibc, or any OS utilities.

**Base image comparison:**

| Base | Size | Has shell | Package manager | Use when |
|---|---|---|---|---|
| `scratch` | 0 | ❌ | ❌ | Static Go/Rust binaries |
| `alpine` | ~5MB | ✅ (sh) | ✅ (apk) | Most apps — tiny, still debuggable |
| `debian-slim` | ~80MB | ✅ | ✅ (apt) | When alpine has glibc compatibility issues |
| `ubuntu` | ~80MB | ✅ | ✅ (apt) | Full OS tooling needed |
| Full language base | 300MB+ | ✅ | ✅ | Never in production |

**Security bonus:** a `scratch` container has no shell. If an attacker exploits it, they land inside a binary with nothing to work with — no `bash`, no `curl`, no `apt`. That's a real security improvement for public-facing services.

**Why image size matters in ECS/EKS:**
```
300MB image → scale-out event → EC2 node pulls from ECR → 30-60 second cold start
 10MB image → same event                                → 2-3 second cold start
```
During a traffic spike when you need 20 new containers immediately, that difference is felt.

### 4. Build multiple images from one Dockerfile

Sometimes a single repo produces multiple artifacts — a server binary and a client binary, or multiple microservices that share build dependencies. Instead of maintaining separate Dockerfiles and re-downloading the entire dependency tree multiple times, define multiple named final stages in one file:

```dockerfile
# Shared build stage — compiled once, reused by both finals
FROM golang:1.20-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /bin/server ./cmd/server
RUN CGO_ENABLED=0 go build -o /bin/client ./cmd/client

# Final image 1: just the server
FROM scratch AS run-server
COPY --from=builder /bin/server /bin/server
ENTRYPOINT ["/bin/server"]

# Final image 2: just the client
FROM scratch AS run-client
COPY --from=builder /bin/client /bin/client
ENTRYPOINT ["/bin/client"]
```

Build each image separately with `--target`:

```bash
docker build --target run-server -t myapp:server .
docker build --target run-client -t myapp:client .
```

**What makes this efficient:** when you run the second `docker build`, the `builder` stage is already cached. Docker skips downloading Go modules and skips compilation — it jumps straight to `FROM scratch AS run-client` and copies the already-built binary. You pay the build cost once; you get two independent production-ready images.

**Real CI pattern:**
```bash
# Both commands below hit the builder cache — total time: ~2 seconds
docker build --target run-server -t $ECR_URL/myapp:server-$SHA .
docker build --target run-client -t $ECR_URL/myapp:client-$SHA .
```

**Interview framing:** "We had 6 Go microservices in one repo — one Dockerfile, 6 `--target` stages. CI produced all 6 images in under 2 minutes because the shared build stage was cached."

### 5. Non-root user

Containers run as root by default. If the container is compromised, the attacker has root on the container filesystem.

```dockerfile
# Alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Debian/Ubuntu
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser
```

In K8s, also enforce at the pod level:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

### 6. .dockerignore

```
# .dockerignore — like .gitignore for docker build context
node_modules/
.git/
*.log
.env
tests/
coverage/
dist/
```

Without this, `docker build .` sends **everything** in the directory to the Docker daemon — including `node_modules` (potentially 1GB+), `.git/`, and `.env` files with secrets. Always include `.dockerignore`.

---

## → How this maps to K8s and AWS

**ENV → K8s ConfigMap / Secret**

In K8s, don't hardcode environment-specific values in the image. Inject at runtime:
```yaml
env:
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: db_host
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: db_password
```

Same image, different config per environment (dev/staging/prod).

**CMD/ENTRYPOINT → K8s command/args**

```yaml
containers:
  - name: app
    image: myapp:1.0
    command: ["node"]        # equivalent to ENTRYPOINT
    args: ["server.js"]      # equivalent to CMD
```

**Multi-stage builds → ECR image size → cold start speed**

Smaller images pull faster from ECR during ECS/EKS scale-out. At a traffic spike, a 10MB image vs 300MB is the difference between new capacity in seconds vs minutes.

**Build multiple images → separate ECR repos, independent deploys**

Each `--target` image gets its own ECR repository and its own ECS task definition or K8s Deployment. The images are independent — roll out `server` without touching `client`, scale them differently, canary them separately.
