# paramiko + psutil — Remote SSH and System Monitoring

## paramiko — SSH from Python

```python
import paramiko, psutil

# Remote SSH command
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.10", username="ubuntu", key_filename="~/.ssh/id_rsa")
stdin, stdout, stderr = client.exec_command("systemctl status nginx")
print(stdout.read().decode())
exit_code = stdout.channel.recv_exit_status()
client.close()

# Local system health snapshot
mem = psutil.virtual_memory()
disk = psutil.disk_usage("/")
print(f"CPU:  {psutil.cpu_percent(interval=1)}%")
print(f"RAM:  {mem.percent}% ({mem.used // 2**30}GB / {mem.total // 2**30}GB)")
print(f"Disk: {disk.percent}% used")
```

---

## paramiko patterns

### Key-based auth

```python
client.connect(
    hostname="10.0.1.50",
    username="ec2-user",
    key_filename="/home/user/.ssh/prod_key.pem",  # path to private key
)
```

### Read stdout/stderr + exit status

```python
stdin, stdout, stderr = client.exec_command("df -h /")
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
rc  = stdout.channel.recv_exit_status()   # blocks until command finishes

if rc != 0:
    raise RuntimeError(f"Remote command failed (rc={rc}): {err}")
```

### SFTP — transfer files over SSH

```python
sftp = client.open_sftp()
sftp.get("/remote/path/file.log", "/local/path/file.log")   # download
sftp.put("/local/config.yml", "/remote/etc/app/config.yml") # upload
sftp.close()
```

### Known-hosts in production

```python
# AutoAddPolicy() skips host key verification — MITM risk
# NEVER use in production automation

# Production pattern — load known_hosts, reject unknown hosts
client.set_missing_host_key_policy(paramiko.RejectPolicy())
client.load_system_host_keys()  # reads ~/.ssh/known_hosts
```

---

## psutil — System monitoring

```python
import psutil

# CPU
psutil.cpu_percent(interval=1)     # blocks 1s, returns usage % (all cores avg)
psutil.cpu_count()                 # logical cores
psutil.cpu_count(logical=False)    # physical cores

# Memory
mem = psutil.virtual_memory()
mem.total    # bytes
mem.used
mem.available
mem.percent  # used %

# Disk
disk = psutil.disk_usage("/")
disk.total
disk.used
disk.free
disk.percent

# Network I/O (cumulative counters since boot)
net = psutil.net_io_counters()
net.bytes_sent
net.bytes_recv
net.packets_sent
net.packets_recv

# Per-interface
per_iface = psutil.net_io_counters(pernic=True)
eth0 = per_iface["eth0"]
```

### Process inspection

```python
# Iterate all processes
for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
    try:
        info = proc.info
        if info["cpu_percent"] > 50:
            print(f"High CPU: {info['name']} (pid {info['pid']})")
    except psutil.NoSuchProcess:
        pass  # process died mid-iteration

# Find a specific process
matching = [p for p in psutil.process_iter(["name"]) if "nginx" in p.info["name"]]
```

### Health check script pattern

```python
def system_ok(cpu_threshold=80, mem_threshold=90, disk_threshold=85):
    alerts = []
    if psutil.cpu_percent(interval=1) > cpu_threshold:
        alerts.append("CPU high")
    if psutil.virtual_memory().percent > mem_threshold:
        alerts.append("RAM high")
    if psutil.disk_usage("/").percent > disk_threshold:
        alerts.append("Disk high")
    return alerts
```

---

## Interview angle

**In the HR screen:** "Have you used paramiko?" → Yes, for running commands on remote servers without leaving Python — useful for scripts that SSH into a box to collect health data or restart a service.

**Follow-up ready:**
- "Why not subprocess + ssh?" → paramiko avoids shell escaping issues and works without ssh binary on the host; also easier to handle stdin/stdout programmatically
- "When would you use Ansible instead?" → paramiko for ad-hoc Python automation; Ansible when you need idempotent, declarative config management across many hosts
- "psutil in prod?" → lightweight polling for alerting sidecars, k8s liveness scripts, or pre-flight checks before deployments
