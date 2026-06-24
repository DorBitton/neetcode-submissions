# Docker Networking

> By default, containers are isolated — sealed boxes. Docker networking is the wiring that decides who can talk to whom.

---

## The mental model

Think of Docker's bridge network as a private office floor. Containers on the same floor can reach each other freely. Containers on a different floor can't. The host machine is the building lobby — it connects to the outside world, and you control which rooms have a phone extension (port) that outsiders can dial.

```
                    Outside world (your browser, the internet)
                             │
                    Host machine (your laptop or EC2)
                        │         │
                  Port 8080  Port 5432           ← only exposed ports are reachable
                        │         │
                   Container A   Container B      ← bridge network: can talk to each other
                                                  ← Container C (different network): isolated
```

```
Host machine
├── Container A (bridge network)   ─────────┐
├── Container B (bridge network)   ─────────┤── can reach each other
├── Container C (different network) ─────────── cannot reach A or B
└── Host port 8080 ────────────────────────────── forwards to Container A :80
```

---

## Port forwarding — exposing containers to the host

Containers run in their own network namespace. To reach a container from your browser or from outside the host, you map a **host port** to a **container port**.

**The hotel switchboard analogy:** the hotel has many rooms (containers) each with an internal phone extension. Outsiders call the main number and ask for a specific extension. Port forwarding is the switchboard — incoming calls on port 8080 get transferred to the container's port 80.

```bash
docker run -p 8080:80 nginx        # host port 8080 → container port 80
docker run -p 443:443 -p 80:80 nginx   # multiple ports
docker run -p 127.0.0.1:8080:80 nginx  # bind to localhost only (not externally)
docker run -P nginx                    # map all EXPOSE'd ports to random host ports
```

```
Browser → localhost:8080 → Docker → container:80 → nginx
```

**EXPOSE in Dockerfile vs -p at runtime:**
```
EXPOSE 80       → documentation only — tells readers "this container listens on 80"
                  does NOT actually open any port
-p 8080:80      → actually opens the port on the host
```

`EXPOSE` without `-p` is like a comment. `-p` is what actually opens it.

```bash
docker port <container>            # see what ports are mapped
```

---

## Network drivers

### bridge (default) — isolated private network

Every container you run without specifying `--network` goes on the default bridge network.

```bash
docker network ls                  # list networks
docker run nginx                   # → default bridge network
docker network inspect bridge      # see which containers are on it
```

**Default bridge limitations:**
- Containers can reach each other by IP only (no DNS)
- All containers share one big network — no isolation between apps

**User-defined bridge — what you should actually use:**
```bash
docker network create myapp-net
docker run --network myapp-net --name db postgres
docker run --network myapp-net --name web nginx

# Now web can reach db by name:
docker exec web ping db            # works — Docker provides DNS on user-defined networks
```

User-defined bridge networks have **built-in DNS** — containers reach each other by container name. The default bridge doesn't.

### host — no network isolation

Container shares the host's network stack directly. No NAT, no port mapping needed.

```bash
docker run --network host nginx    # nginx binds directly to host :80
```

```
Normally:    Browser → host:8080 → NAT → container:80
With host:   Browser → host:80 → nginx (running in container, same namespace)
```

**Use cases:** high-performance networking, when you need the actual host IP, low-level network tools.
**Not available on Docker Desktop (Mac/Windows)** — only works on Linux.

### none — completely isolated

No networking at all. Used for batch jobs that don't need network access.

```bash
docker run --network none myapp
```

### overlay — multi-host networking

Connects containers across **multiple Docker hosts**. This is Docker Swarm territory and the foundation for K8s networking.

```
Host 1: Container A ──┐
                      ├── overlay network (VXLAN tunnel) ── communicate across hosts
Host 2: Container B ──┘
```

You won't use overlay directly — K8s CNI plugins (Calico, Flannel, Cilium) implement this concept for the cluster network.

---

## Container DNS and service discovery

On user-defined networks, Docker runs an internal DNS server:

```bash
docker network create app-net
docker run -d --name db --network app-net postgres
docker run -d --name api --network app-net myapi

# Inside the api container:
# DB_HOST=db   ← just use the container name
# Docker DNS resolves "db" → 172.18.0.2 automatically
```

This is how multi-container apps find each other without hardcoding IPs.

---

## Common commands

```bash
# Networks
docker network ls                           # list all networks
docker network create mynet                 # create a bridge network
docker network create --driver overlay mynet  # overlay network
docker network inspect mynet               # details: which containers, IPs
docker network connect mynet container1    # add running container to network
docker network disconnect mynet container1 # remove from network
docker network rm mynet                    # delete network

# Container connectivity
docker run --network mynet --name web nginx
docker exec web curl http://db:5432        # test DNS resolution
docker exec web ping api                   # test reachability by name
```

---

## ## Interview questions

**"Two containers on the same bridge network can't reach each other by name — why?"**
→ The default bridge network has no DNS. Create a user-defined bridge (`docker network create`) — that gives you automatic DNS resolution by container name.

**"What's the difference between EXPOSE and -p?"**
→ `EXPOSE` is documentation only (tells readers the intended port). `-p` actually opens the port on the host. You need `-p` to make a container reachable from outside.

**"How do containers talk to each other in production?"**
→ In Docker: user-defined bridge network + container names as hostnames. In K8s: Services — each pod gets a ClusterIP Service, other pods reach it by service name via cluster DNS.

---

## → How this maps to K8s and AWS

**Port forwarding → K8s Service**

In K8s, you don't use `-p` flags. Instead you create a **Service** that exposes pods:

```yaml
# Equivalent of docker run -p 80:8080
apiVersion: v1
kind: Service
spec:
  type: LoadBalancer           # ClusterIP (internal) / NodePort / LoadBalancer (external)
  ports:
    - port: 80                 # external port
      targetPort: 8080         # container port
```

| Docker | K8s Service type |
|---|---|
| `localhost` only | `ClusterIP` (cluster-internal only) |
| `-p <hostPort>:<containerPort>` | `NodePort` (each node's IP + port) |
| ALB in front | `LoadBalancer` (cloud LB, e.g. AWS ALB) |

**Bridge network → K8s pod network**

Each pod in K8s gets its own IP (like a container on a bridge network). Pods on the same cluster can reach each other by pod IP. Services provide a stable DNS name (like container names on user-defined bridge networks).

**Container name DNS → K8s Service DNS**

```
Docker: container name → DNS → IP
K8s:    service name → DNS → ClusterIP → pod IPs
```

In K8s, you connect to `http://db-service:5432` — same concept, but the DNS resolves to a Service which load-balances across multiple DB pods.

**Overlay network → K8s CNI**

K8s uses a Container Network Interface (CNI) plugin (Calico, Flannel, Cilium, AWS VPC CNI) to implement the cluster network. It's Docker's overlay concept, but managed by K8s. AWS EKS uses the VPC CNI plugin — each pod gets an actual VPC IP address.
