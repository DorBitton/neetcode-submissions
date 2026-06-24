# Dockerfiles — Building Images

> The recipe for your image. Every instruction is a layer.

---

## Dockerfile structure

```dockerfile
# Base image — always start from something
FROM node:20-alpine

# Metadata (optional)
LABEL maintainer="dor@company.com"

# Set working directory inside the container
WORKDIR /app

# Copy dependency files first (layer cache trick)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the app
COPY . .

# Runtime environment variable
ENV NODE_ENV=production
ENV PORT=3000

# Expose documents the intended port (doesn't actually open it)
EXPOSE 3000

# What to run when the container starts
CMD ["node", "server.js"]
```

---

## Layer caching — the most important build optimization

Every Dockerfile instruction creates a layer. Docker caches each layer and reuses it on the next build — **unless something above it changed**, which invalidates it and everything below.

### The problem

```dockerfile
FROM golang:1.20-alpine
WORKDIR /src
COPY . .              ← copies ALL source files
RUN go mod download   ← downloads dependencies (30-60 seconds)
RUN go build -o /bin/server ./cmd/server
```

What happens when you change one line in `main.go`:

```
Layer: FROM golang:1.20-alpine    ✅ cache hit
Layer: WORKDIR /src               ✅ cache hit
Layer: COPY . .                   ❌ cache miss — main.go changed
Layer: RUN go mod download        ❌ must re-run (60 seconds wasted)
Layer: RUN go build               ❌ must re-run
```

`go mod download` re-runs on **every single build**, even if `go.mod` never changed. You're re-downloading all dependencies because you changed a comment.

### The fix — separate what changes at different rates

```dockerfile
FROM golang:1.20-alpine
WORKDIR /src
COPY go.mod go.sum ./   ← only the dependency manifest (rarely changes)
RUN go mod download     ← cached until go.mod/go.sum actually changes
COPY . .                ← source code (changes constantly)
RUN go build -o /bin/server ./cmd/server
```

What happens now when you change `main.go`:

```
Layer: FROM golang:1.20-alpine    ✅ cache hit
Layer: WORKDIR /src               ✅ cache hit
Layer: COPY go.mod go.sum ./      ✅ cache hit (go.mod didn't change)
Layer: RUN go mod download        ✅ cache hit — SKIPPED (60 seconds saved)
Layer: COPY . .                   ❌ cache miss — expected, code changed
Layer: RUN go build               ❌ must re-run — expected
```

Dependencies only re-download when `go.mod` or `go.sum` actually changes.

### The mental model — pyramid of change frequency

```
RARELY CHANGES                        put near the top
──────────────────────────────────────────────────────
FROM base image
OS packages (apt-get install)
Language runtime
Dependency manifest (go.mod, package.json, requirements.txt)
Dependencies installed (go mod download, npm ci, pip install)
──────────────────────────────────────────────────────
CONSTANTLY CHANGES                    put near the bottom
Your source code (COPY . .)
Build step (go build, npm run build)
```

**Rule:** the higher in the Dockerfile, the less often it should change.

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

### Why this matters in real life

In CI/CD, every push triggers a build. Without caching optimization:
```
Every push:  3-5 min (downloading all deps every time)
```

With caching:
```
Code change:   20-30 sec (deps cached, only recompile)
go.mod change: 3-5 min   (deps must re-download — expected and correct)
```

50 engineers pushing 5 times/day × 4 minutes saved = **16+ hours of CI time saved per day**.

**In interviews:** "how would you reduce CI build times?" → layer cache ordering is the first answer.

---

## COPY vs ADD

Both copy files into the image. **Default to COPY. ADD has hidden magic.**

| | `COPY` | `ADD` |
|---|---|---|
| Copy local files | ✅ | ✅ |
| Copy from URL | ❌ | ✅ (downloads it) |
| Auto-extract tar archives | ❌ | ✅ (extracts automatically) |
| Predictable behavior | ✅ | ⚠️ (the tar magic surprises people) |

```dockerfile
COPY app.py /app/           # explicit, predictable
COPY src/ /app/src/
COPY package*.json ./       # glob works

ADD https://example.com/file.tar.gz /tmp/    # downloads and extracts — use only for this
ADD app.tar.gz /app/                         # extracts tar — rarely what you want
```

**Rule:** use `COPY` unless you specifically need `ADD`'s URL download or tar extraction. Using `ADD` for regular files is a Dockerfile smell.

---

## CMD vs ENTRYPOINT

The most common Dockerfile interview question. Both define what runs when a container starts. The difference is how they interact with arguments.

### CMD — the default command (overridable)

```dockerfile
CMD ["node", "server.js"]
```

```bash
docker run myapp                    # runs: node server.js
docker run myapp node --version     # overrides CMD entirely: runs node --version
```

CMD is completely replaced if you pass a command to `docker run`. Use it when you want a sensible default that users might override.

### ENTRYPOINT — the fixed executable (not overridable)

```dockerfile
ENTRYPOINT ["node"]
```

```bash
docker run myapp                    # runs: node   (needs CMD or an argument)
docker run myapp server.js          # runs: node server.js
docker run myapp --version          # runs: node --version
```

Arguments to `docker run` are appended to ENTRYPOINT, not replace it. The container always runs `node something`.

### ENTRYPOINT + CMD together — the standard pattern

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js"]
```

```bash
docker run myapp                    # runs: node server.js   (CMD is the default arg)
docker run myapp other.js           # runs: node other.js    (CMD is overridden)
docker run --entrypoint python myapp script.py  # override ENTRYPOINT entirely
```

**Mental model:**
```
ENTRYPOINT = the executable (what the container IS)
CMD        = the default arguments (what it does by default)
```

**When to use which:**
```
CMD only        → flexible: a general-purpose image where the command varies
ENTRYPOINT only → strict: the container is one specific tool (e.g. a CLI wrapper)
ENTRYPOINT+CMD  → best of both: fixed executable, overridable default args
```

### Shell form vs Exec form

```dockerfile
# Shell form (DON'T use for ENTRYPOINT/CMD)
CMD node server.js              # runs as: /bin/sh -c "node server.js"

# Exec form (DO use)
CMD ["node", "server.js"]       # runs directly, no shell wrapper
```

**Why exec form matters:** with shell form, `docker stop` sends SIGTERM to `/bin/sh`, not to your app. Your app never gets the signal and is eventually killed with SIGKILL after the grace period. Exec form sends signals directly to your process.

---

## Environment Variables — ENV and ARG

### ENV — runtime variables (persisted in the image)

```dockerfile
ENV NODE_ENV=production
ENV DB_HOST=localhost
ENV DB_PORT=5432
```

Available during build and at runtime inside the container.

```bash
docker run -e NODE_ENV=staging myapp        # override at runtime
docker run --env-file .env myapp            # load from file
```

```bash
docker inspect myapp | grep -A5 Env        # see what ENVs are set
```

### ARG — build-time only (not persisted)

```dockerfile
ARG APP_VERSION=1.0
RUN echo "Building version $APP_VERSION"
```

```bash
docker build --build-arg APP_VERSION=2.0 .
```

ARG values are NOT available in the running container. Use them for build-time configuration (version numbers, build flags).

**Security:** don't use ARG for secrets — they appear in `docker history`. Use secrets management at runtime instead.

---

## Dockerfile best practices

### 1. Use a minimal base image

```dockerfile
# ❌ Big
FROM ubuntu:22.04

# ✅ Much smaller
FROM python:3.11-alpine          # alpine = minimal Linux (~5MB vs ~70MB)
FROM python:3.11-slim            # slim = stripped debian (~45MB)
FROM node:20-alpine
```

### 2. Layer cache ordering — least changed to most changed

```dockerfile
# ❌ Bad — app code changes, so ALL layers below rebuild every time
FROM node:20-alpine
COPY . .
RUN npm install

# ✅ Good — dependencies cached separately from code
FROM node:20-alpine
COPY package*.json ./      ← only changes when deps change
RUN npm ci
COPY . .                   ← changes every time, but only this layer rebuilds
```

### 3. Combine RUN commands to reduce layers

```dockerfile
# ❌ 3 layers
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ 1 layer, same result
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

### 4. Multi-stage builds — don't ship build tools

The problem: compiling Go/Java/Rust/TypeScript requires a compiler, build tools, and source code. None of that should be in a production image. Multi-stage builds solve this by using one image to build and a different, minimal image to run.

```dockerfile
# Stage 1: build (big image, has compiler)
FROM golang:1.20-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o /bin/server ./cmd/server

# Stage 2: runtime (tiny image, has nothing but the binary)
FROM scratch
COPY --from=builder /bin/server /bin/server
ENTRYPOINT ["/bin/server"]
```

`COPY --from=builder` pulls a file from a previous stage into the current one. The final image contains **only what you COPY into it** from prior stages. No compiler, no source code, no Go runtime, no shell — just the binary.

### FROM scratch — the empty image

`scratch` is a special Docker keyword meaning "start from nothing." Literally an empty filesystem.

```
FROM golang:1.20-alpine   → ~250MB (Go compiler + Alpine Linux)
FROM alpine               → ~5MB   (minimal Linux, has shell, package manager)
FROM scratch              → 0MB    (truly empty — no OS at all)
```

**This only works for statically compiled binaries.** Go (with CGO disabled) and Rust compile to a single self-contained binary with no external library dependencies. The binary runs on any Linux kernel without needing libc, glibc, or any OS utilities.

```bash
# Go: build a static binary (no external dependencies)
CGO_ENABLED=0 go build -o /bin/server ./cmd/server
```

The result:

```
golang:1.20-alpine + your app    → ~300MB
scratch + your compiled binary   → ~10MB   (just the binary itself)
```

A 30x size reduction. And this is what the KillerCoda scenario is asking you to build.

### Base image comparison — choose the right runtime base

| Base | Size | Has shell | Has package manager | Use when |
|---|---|---|---|---|
| `scratch` | 0 | ❌ | ❌ | Statically compiled Go/Rust binaries |
| `alpine` | ~5MB | ✅ (sh) | ✅ (apk) | Most apps — tiny, debuggable |
| `debian-slim` | ~80MB | ✅ | ✅ (apt) | When alpine has glibc compatibility issues |
| `ubuntu` | ~80MB | ✅ | ✅ (apt) | When you need full OS tooling |
| Full language image | 300MB+ | ✅ | ✅ | Never in production |

### Security angle — scratch has no attack surface

```
FROM ubuntu-based image:
  Has bash → attacker can exec in and run commands
  Has curl/wget → attacker can download tools
  Has apt → attacker can install packages
  Has /etc/passwd, cron, sshd...

FROM scratch:
  No shell → docker exec -it container bash → Error: no such file
  No package manager
  No utilities
  Just your binary
```

If a container running on `scratch` is compromised, the attacker is inside a binary with nothing else available. This is a meaningful security improvement, especially for public-facing services.

### Named stages and --target

```dockerfile
FROM golang:1.20 AS deps
COPY go.mod go.sum ./
RUN go mod download

FROM deps AS builder          # ← build on top of deps stage
COPY . .
RUN go build -o /bin/server .

FROM scratch AS production    # ← final runtime
COPY --from=builder /bin/server /bin/server
ENTRYPOINT ["/bin/server"]
```

```bash
# Build only up to a specific stage (useful in CI)
docker build --target builder -t myapp:builder .   # stop at builder stage
docker build --target production -t myapp:prod .   # full build
```

`--target` is useful in CI pipelines when you want to run tests inside the builder stage before producing the final image.

### Real-world size comparison (Go example)

```bash
docker build -t server-1 .                     # before (no multi-stage, full golang base)
docker build -t server-2 -f Dockerfile.multi . # after (multi-stage + scratch)

docker images | grep server
# server-1    300MB+
# server-2    ~10MB
```

In ECS/EKS, an EC2 node that needs to pull `server-1` during a scale-out event takes 30-60 seconds. `server-2` takes 2-3 seconds. During a traffic spike, that difference matters.

### 5. Non-root user

```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

Running as root inside a container is a security risk. If the container is compromised, the attacker has root on the container filesystem.

### 6. .dockerignore

```
# .dockerignore
node_modules/
.git/
*.log
.env
tests/
```

Like `.gitignore` for Docker. Prevents large/sensitive files from being sent to the Docker daemon during `docker build`.

---

## → How this maps to K8s and AWS

**ENV → K8s ConfigMap / Secret**

In K8s, you don't hardcode ENV values in the Dockerfile for prod. Instead:
```yaml
# K8s passes env vars from ConfigMap/Secret at runtime
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

This keeps the image portable — same image, different config per environment.

**CMD/ENTRYPOINT → K8s command/args**

```yaml
# Equivalent in K8s Pod spec
containers:
  - name: app
    image: myapp:1.0
    command: ["node"]        # = ENTRYPOINT
    args: ["server.js"]      # = CMD
```

**Multi-stage builds → ECR image size**

Smaller images pull faster in ECS/EKS, especially during scale-out events when new EC2 nodes need to pull the image before they can serve traffic. A 50MB image vs a 500MB image is a real cold-start difference at scale.
