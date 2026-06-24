# Docker Volumes and Storage

> Containers are ephemeral — their filesystem vanishes when they're removed. Volumes are the USB drives you plug into them: data lives on the drive, not the container. Swap the container, plug in the same drive — your data is still there.

---

## The problem

```bash
docker run postgres                # database starts, you write data
docker stop <container>            # container stops
docker rm <container>              # container deleted — ALL DATA GONE
docker run postgres                # fresh container — empty database
```

By default, **everything written inside a container is lost when it's removed.** Volumes and bind mounts are the solution.

---

## Three storage options

```
Option A: Container filesystem     ← data lost on container removal
Option B: Volume                   ← Docker-managed, persists across containers
Option C: Bind mount               ← host directory, mounted into the container
```

---

## Volumes — Docker-managed persistence

Volumes are managed by Docker. Docker decides where they live on the host (`/var/lib/docker/volumes/` on Linux). You don't need to care about the exact path.

```bash
# Create a volume
docker volume create mydata

# Use a volume (creates it if it doesn't exist)
docker run -v mydata:/var/lib/postgresql/data postgres
docker run --mount type=volume,source=mydata,target=/var/lib/postgresql/data postgres

# Inspect
docker volume ls                           # list all volumes
docker volume inspect mydata               # see where it lives on host
docker volume rm mydata                    # delete volume (and its data)
docker volume prune                        # delete all unused volumes
```

**What makes volumes the right choice for production data:**
- Survive container removal — data persists even after `docker rm`
- Easy to back up, restore, migrate
- Can be shared between containers
- Work the same way on any OS (Docker Desktop on Mac/Windows abstracts the host path)
- Docker handles permissions

```bash
# Share a volume between containers (e.g., nginx serving files from app container)
docker run -v shared:/output myapp          # app writes to /output
docker run -v shared:/usr/share/nginx/html nginx  # nginx serves those files
```

---

## Bind mounts — host directory into the container

You choose the exact host path. The container sees it as if it's part of its own filesystem.

```bash
docker run -v /host/path:/container/path nginx
docker run -v $(pwd):/app myapp                     # current directory → /app in container
docker run --mount type=bind,source=$(pwd),target=/app myapp
```

**The development superpower:** edit code on your host, container sees changes instantly — no rebuild needed.

```bash
# Development workflow
docker run -v $(pwd):/app -p 3000:3000 node:20 node /app/server.js
# Edit server.js on your laptop → container sees it → restart and it runs your new code
```

**Production considerations:** bind mounts expose the host filesystem. Container has access to whatever you mount — including sensitive directories if you make a mistake. In prod, use volumes.

---

## Volumes vs Bind mounts — when to use which

| | Volume | Bind mount |
|---|---|---|
| Who manages the path | Docker | You |
| Works on Mac/Windows | ✅ (Docker abstracts it) | ✅ (but path must exist) |
| Best for production data | ✅ | ❌ |
| Best for dev (live code) | ❌ | ✅ |
| Share between containers | ✅ | ✅ |
| Easy to back up | ✅ (docker volume cp) | ✅ (it's just files) |
| Permissions handled | Docker | You |

**Rule of thumb:**
- **Development:** bind mount your source code so changes reflect immediately
- **Production data (databases, uploads, logs):** named volumes
- **Config files in prod:** bind mount read-only config (`-v /etc/myapp.conf:/etc/myapp.conf:ro`)

---

## Read-only mounts

```bash
docker run -v myconfig:/etc/nginx/nginx.conf:ro nginx    # :ro = read-only
docker run -v $(pwd)/config:/config:ro myapp
```

Container can read the files but can't modify them. Good for config files you don't want the container to accidentally overwrite.

---

## tmpfs — in-memory, never touches disk

```bash
docker run --tmpfs /tmp myapp
docker run --mount type=tmpfs,target=/tmp myapp
```

Data in tmpfs is in RAM only. Gone when the container stops. Use for sensitive temporary data (secrets, session data) that should never be written to disk.

---

## Common commands

```bash
docker volume create mydata
docker volume ls
docker volume inspect mydata
docker volume rm mydata
docker volume prune                     # remove unused volumes

docker run -v mydata:/data alpine       # named volume
docker run -v $(pwd):/app alpine        # bind mount
docker run --tmpfs /tmp alpine          # tmpfs
docker run -v mydata:/data:ro alpine    # read-only
```

---

## Interview questions

**"What happens to data when you remove a container?"**
→ Lost — the container's writable layer is deleted. Data needs to live in a volume (or bind mount) to persist.

**"When would you use a bind mount vs a named volume?"**
→ Bind mount in development: mount your source code so changes reflect inside the container without rebuilding. Named volume in production: databases, uploads, any data that must outlive the container. Bind mounts expose the host filesystem, which is a security concern in prod.

**"How do you share data between two containers?"**
→ Mount the same named volume in both: `docker run -v shared:/data container-a` and `docker run -v shared:/data container-b`. Both see the same files.

---

## → How this maps to K8s and AWS

**Volume → K8s PersistentVolume (PV) + PersistentVolumeClaim (PVC)**

In K8s, "volumes" are more complex because data needs to survive pods being rescheduled to different nodes:

```yaml
# The equivalent of docker run -v mydata:/data
apiVersion: v1
kind: PersistentVolumeClaim
spec:
  storageClassName: gp2          # AWS EBS gp2 disk
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
---
# In the Pod:
volumes:
  - name: mydata
    persistentVolumeClaim:
      claimName: my-pvc
containers:
  - volumeMounts:
      - name: mydata
        mountPath: /data
```

AWS EKS typically uses EBS volumes (like a physical disk attached to one node) or EFS (like NFS, can be shared across nodes).

**Bind mount for config → K8s ConfigMap**

Instead of bind-mounting a config file, K8s mounts a ConfigMap as a file:

```yaml
# Equivalent of: docker run -v myapp.conf:/etc/myapp.conf:ro myapp
volumes:
  - name: config
    configMap:
      name: myapp-config
containers:
  - volumeMounts:
      - name: config
        mountPath: /etc/myapp.conf
        subPath: myapp.conf
        readOnly: true
```

**tmpfs → K8s emptyDir with medium: Memory**

```yaml
volumes:
  - name: tmp
    emptyDir:
      medium: Memory             # RAM-backed, never hits disk
```

**The key mental shift from Docker to K8s:**
In Docker, volumes live on the host. In K8s, pods move between nodes — so storage must come from outside the node (EBS, EFS, NFS). K8s handles the attach/detach automatically when pods are rescheduled.
