# paramiko + psutil — Remote SSH and System Monitoring

## paramiko — What it is

paramiko is a Python library that implements the SSH protocol in pure Python. It lets you
connect to remote servers and run commands, transfer files, or open interactive shells —
all from a Python script, without shelling out to the `ssh` command-line tool.

### Why use paramiko instead of `subprocess.run(['ssh', ...])`?

`subprocess + ssh` works for simple cases, but has real limitations in production scripts:

- You need the `ssh` binary installed and available in `PATH` on the machine running the script
- Handling stdin/stdout/stderr through subprocess is awkward — you get raw bytes and
  have to manage buffering yourself
- Dealing with passwords or key passphrases requires expect-style hacks or prompts
- Error handling is less granular — you get a return code, not structured exceptions
- There's no clean way to do SFTP file transfers without calling a separate binary

paramiko gives you full programmatic control over the SSH connection. You open it,
run commands, read output, check exit codes, transfer files, and close it — all in Python
with proper exception handling.

---

## 1. Basic connection and command execution

Walk through each line — nothing here is "obvious":

```python
import paramiko

client = paramiko.SSHClient()
# Creates an SSH client object.
# No connection is made yet — this is just the object that will manage the connection.
# Think of it like creating a requests.Session() before calling session.get().

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# SSH verifies the server's identity using its host key — similar to how HTTPS uses
# certificates to verify you're talking to the right server.
# When you connect for the first time, the server's key is not in your known_hosts file.
# This policy setting controls what happens in that case.
#
# AutoAddPolicy() = automatically trust and accept any host key you haven't seen before.
#
# SECURITY WARNING: AutoAddPolicy() is vulnerable to man-in-the-middle attacks.
# If someone intercepts the connection and presents a fake key, paramiko will accept it.
# Fine for scripts running in controlled, trusted environments (your own VPC, lab, CI).
# Never use AutoAddPolicy() in production automation talking to external hosts.

client.connect("192.168.1.10", username="ubuntu", key_filename="~/.ssh/id_rsa")
# Establishes the TCP connection and performs the SSH handshake.
# hostname: the IP or hostname of the remote server
# username: the Unix account to log in as
# key_filename: path to your PRIVATE key file on the local machine.
#   The server must have the matching PUBLIC key in ~/.ssh/authorized_keys for this user.
#
# Other auth options: password="secret" (not recommended), or no key_filename if your
# key is loaded in an SSH agent (paramiko checks the agent automatically).

stdin, stdout, stderr = client.exec_command("systemctl status nginx")
# Runs a single command on the remote server.
# Returns three file-like objects — they work similarly to file handles:
#   stdin  = for sending input TO the command (rarely needed for non-interactive commands)
#   stdout = the command's standard output (what it prints normally)
#   stderr = the command's standard error (what it prints for errors/warnings)
#
# Important: exec_command() returns immediately. The command runs asynchronously.
# The actual output arrives as you read from stdout/stderr.

output = stdout.read().decode()
# stdout is a bytes object — SSH sends raw bytes over the wire.
# .read() reads ALL of the output and returns it as bytes.
#   WARNING: .read() blocks until the command finishes AND closes its stdout channel.
#   This is fine for short commands. For long-running commands, see the interview notes
#   section below about reading in chunks.
# .decode() converts bytes to a Python str using UTF-8 by default.

exit_code = stdout.channel.recv_exit_status()
# Gets the exit code of the remote command (0 = success, non-zero = error).
#
# CRITICAL ORDER: always read stdout AND stderr BEFORE calling recv_exit_status().
#
# Why the order matters — deadlock scenario:
# The remote command writes a lot of output. The SSH channel has a buffer (maybe 64KB).
# If the buffer fills, the remote process blocks waiting for you to read some output.
# Meanwhile, you're blocked in recv_exit_status() waiting for the command to finish.
# Neither side can proceed. This is a deadlock.
# Avoid it by reading stdout and stderr first (draining the buffers), THEN getting the exit code.

client.close()
# Closes the SSH connection and frees the TCP socket.
# Always close connections — in a long-running script, unclosed connections accumulate.
# Use try/finally or a context manager to ensure close() runs even if an exception occurs.
```

---

## 2. Production pattern — read stdout, stderr, and exit code safely

```python
import paramiko

def run_remote(host, user, key_path, command):
    """Run a command on a remote host and return (stdout, stderr, exit_code)."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, key_filename=key_path)
        stdin, stdout, stderr = client.exec_command(command)

        # Read BOTH stdout and stderr before getting the exit code.
        # If the command produces output on both channels, you must drain both
        # to avoid the deadlock described above.
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()

        # Now safe to get the exit code — output has been fully read.
        rc = stdout.channel.recv_exit_status()

        if rc != 0:
            raise RuntimeError(f"Remote command failed (rc={rc}): {err}")

        return out, err, rc

    finally:
        client.close()     # runs whether or not an exception occurred
```

---

## 3. Key-based authentication

SSH key auth works using a matched key pair:

- **Private key** — stays on your machine, never leaves, never shared. Usually stored at
  `~/.ssh/id_rsa` or `~/.ssh/id_ed25519`. Must be kept secret (treat like a password).
- **Public key** — the counterpart you put on remote servers, in `~/.ssh/authorized_keys`
  for the target user. Safe to share — it's useless without the private key.

When you connect, the server sends you a challenge encrypted with your public key. Only
someone with the matching private key can decrypt and answer it. The private key is never
transmitted — the protocol proves you have it without sending it.

```python
client.connect(
    hostname="10.0.1.50",
    username="ec2-user",
    key_filename="/home/user/.ssh/prod_key.pem",  # path to your private key on this machine
    # timeout=10,                                  # optional: TCP connection timeout in seconds
)
```

For EC2 instances, AWS gives you a `.pem` file when you create a key pair. That's your
private key. The corresponding public key is automatically placed in the instance's
`~/.ssh/authorized_keys` by AWS during launch.

---

## 4. SFTP — transferring files over SSH

SFTP (SSH File Transfer Protocol) is a file transfer subsystem that runs over the same SSH
connection. It's not FTP — it's a completely different protocol that happens to use SSH for
encryption and authentication.

`open_sftp()` opens an SFTP session on the existing SSH connection. You don't need to
re-authenticate — it reuses the connection you already established.

```python
client.connect("10.0.1.50", username="ec2-user", key_filename="~/.ssh/prod.pem")

sftp = client.open_sftp()
# Opens the SFTP subsystem on the existing connection — no new auth needed.

sftp.get("/remote/path/app.log", "/local/path/app.log")
# Downloads a file FROM the remote server TO the local machine.
# First arg = remote path (on the server).
# Second arg = local path (on the machine running this script).

sftp.put("/local/config.yml", "/remote/etc/app/config.yml")
# Uploads a file FROM the local machine TO the remote server.
# First arg = local path.
# Second arg = remote path (must have write permission on the remote).

sftp.close()
# Always close the SFTP session when done.
# The underlying SSH connection (client) stays open — you can still run exec_command() after.

client.close()
```

---

## 5. Production host key verification

`AutoAddPolicy()` is convenient for development but dangerous in production. Here's why:

**The threat:** a man-in-the-middle attack means someone has positioned a malicious server
between your script and the real server. Your script connects to the attacker's server
thinking it's the real one. Without host key verification, paramiko trusts it. Now the
attacker can:

- See all commands you run
- See all output (including secrets you print or passwords in command output)
- Modify commands before forwarding them
- Intercept files you transfer

**The defense:** maintain a list of known, trusted host keys. When you connect, verify the
server's key matches what you expect. Reject connections to unknown servers.

```python
# Production pattern — strict host key verification
client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.RejectPolicy())
# RejectPolicy = if the server's key is not in known_hosts, REFUSE the connection and raise an exception.
# This is the safe default for production.

client.load_system_host_keys()
# Reads ~/.ssh/known_hosts and populates paramiko's internal key store.
# After this, paramiko will accept servers whose keys are listed there
# and reject all others (because of RejectPolicy above).

# To add a new server to known_hosts, run manually from the terminal first:
#   ssh user@new-server
# SSH will prompt you to verify the host key fingerprint, then save it.
# After that, your paramiko script can connect to it securely.
```

---

## psutil — What it is

psutil (process and system utilities) is a Python library for querying system resources:
CPU, memory, disk, network, and running processes. It queries the OS kernel directly and
returns structured Python objects.

The key advantage over parsing `/proc` or running shell commands: the same Python code
works on **Linux, macOS, and Windows**. It's useful for health check scripts, monitoring
sidecars, pre-flight checks before deployments, and lightweight alerting.

---

## 6. CPU

```python
import psutil

usage = psutil.cpu_percent(interval=1)
# Samples CPU usage over a time window.
#
# interval=1: blocks for 1 second, measures CPU usage during that second.
# This gives you a meaningful average — not a meaningless instantaneous snapshot.
#
# COMMON GOTCHA: calling cpu_percent(interval=0) or cpu_percent() on the FIRST call
# always returns 0.0. It works by comparing two samples. Without a prior sample to compare
# against, there's nothing to compare. Either:
#   (1) use interval=1 (blocks, but accurate immediately), OR
#   (2) call cpu_percent() once to establish a baseline, wait, then call it again.

print(f"CPU: {usage}%")

cores_logical = psutil.cpu_count()             # logical cores (includes hyperthreading)
cores_physical = psutil.cpu_count(logical=False)  # physical cores only
# On a 4-core CPU with hyperthreading: logical=8, physical=4
```

---

## 7. Memory

```python
mem = psutil.virtual_memory()
# Returns a named tuple with these fields:

print(f"Total:     {mem.total // 2**30} GB")
# .total = total installed RAM in bytes. // 2**30 converts to gigabytes (2^30 = 1 GiB).

print(f"Used:      {mem.used // 2**30} GB")
# .used = RAM currently in use by processes.

print(f"Available: {mem.available // 2**30} GB")
# .available = RAM that can be given to a process right now, without swapping.
#
# IMPORTANT: available is NOT the same as total - used on Linux.
# Linux counts disk page cache as "used" because it's actively using that memory for
# caching. But that cache is immediately reclaimed when a process needs RAM.
# .available already accounts for this — it's the right number to check when you
# want to know "can I launch this process without the system running out of RAM?"

print(f"Percent:   {mem.percent}%")
# .percent = used / total * 100  (the simple ratio, not the nuanced "available" calculation)
# Use .available for "is the system under memory pressure?" checks.
# Use .percent for dashboards and alerting thresholds.
```

---

## 8. Disk

```python
disk = psutil.disk_usage("/")
# Returns usage for the filesystem that the given path is on.
# "/" = the root filesystem.
#
# IMPORTANT on Linux: different mount points can be separate filesystems.
# /var, /home, /tmp, /data may all be separate partitions or volumes.
# disk_usage("/") tells you about the root partition, NOT /var.
# If your logs are in /var and /var is a separate filesystem, you need:
#   psutil.disk_usage("/var")
#
# Always check the specific path you care about, not just "/".

print(f"Total: {disk.total // 2**30} GB")
print(f"Used:  {disk.used // 2**30} GB")
print(f"Free:  {disk.free // 2**30} GB")
print(f"Used:  {disk.percent}%")
```

---

## 9. Network I/O

```python
net = psutil.net_io_counters()
# Returns cumulative counters since the system booted.
# These numbers only go up — they never reset between calls.
# To measure current throughput, take two samples and compute the difference.

print(f"Bytes sent:    {net.bytes_sent}")
print(f"Bytes received: {net.bytes_recv}")
print(f"Packets sent:  {net.packets_sent}")
print(f"Packets recv:  {net.packets_recv}")

# Per-interface breakdown
per_iface = psutil.net_io_counters(pernic=True)
# Returns a dict: {"eth0": counters, "lo": counters, "eth1": counters, ...}
eth0 = per_iface.get("eth0")
if eth0:
    print(f"eth0 bytes sent: {eth0.bytes_sent}")
```

---

## 10. Process inspection

```python
# Iterate over all running processes
for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
    # process_iter() yields Process objects for every running process.
    #
    # The list argument pre-fetches those specific attributes for each process atomically.
    # This is more efficient than accessing proc.pid, proc.name(), etc. separately,
    # because those would each make a separate /proc read.
    #
    # The attributes land in proc.info as a dict.
    try:
        info = proc.info
        if info["cpu_percent"] and info["cpu_percent"] > 50:
            print(f"High CPU: {info['name']} (pid {info['pid']})")
    except psutil.NoSuchProcess:
        pass
        # Processes can die between when process_iter() lists them and when you
        # access their info. This race condition is normal — always catch NoSuchProcess.
    except psutil.AccessDenied:
        pass
        # Some processes (kernel threads, other users' processes) may not be readable.

# Find a specific process by name
matching = [
    p for p in psutil.process_iter(["name", "pid"])
    if "nginx" in (p.info["name"] or "")
]
print(f"Found {len(matching)} nginx processes")
```

---

## 11. Health check function pattern

```python
def system_ok(cpu_threshold=80, mem_threshold=90, disk_threshold=85, disk_path="/"):
    """
    Check system health. Returns a list of alert strings.
    Empty list = everything is fine.
    """
    alerts = []

    cpu = psutil.cpu_percent(interval=1)
    if cpu > cpu_threshold:
        alerts.append(f"CPU high: {cpu:.1f}% (threshold: {cpu_threshold}%)")

    mem = psutil.virtual_memory()
    # Use mem.percent (used/total) for a general "is this system loaded?" check.
    # Note: mem.available would be more accurate, but percent is what operators expect.
    if mem.percent > mem_threshold:
        alerts.append(f"RAM high: {mem.percent:.1f}% (threshold: {mem_threshold}%)")

    disk = psutil.disk_usage(disk_path)
    if disk.percent > disk_threshold:
        alerts.append(f"Disk high on {disk_path}: {disk.percent:.1f}% (threshold: {disk_threshold}%)")

    return alerts


# Usage
alerts = system_ok()
if alerts:
    print("ALERTS:")
    for alert in alerts:
        print(f"  - {alert}")
else:
    print("System healthy")
```

---

## Interview angle

**In the HR screen:** "Have you used paramiko?" → Yes, for running commands on remote servers
without leaving Python — useful for scripts that SSH into a box to collect health data or
restart a service, especially when you want proper exit code handling and output capture.

**Follow-up questions and answers:**

**"Why not subprocess + ssh?"**
subprocess + ssh works for simple cases, but paramiko avoids shell escaping issues, works
without the `ssh` binary on the host (useful in minimal containers), and gives you cleaner
stdout/stderr handling and proper exception types. You also get SFTP for free on the same
connection.

**"What's the difference between paramiko and Fabric?"**
Fabric is built on top of paramiko and adds higher-level patterns: connection retry, running
the same command on multiple hosts, nicer APIs for common tasks (upload, download, sudo).
Use Fabric when you need to run the same deployment command on 20 servers and want retry
and connection pooling handled for you. Use paramiko directly when you need fine-grained
control — custom channel behavior, tunneling, key management, or embedding SSH in a larger
Python application.

**"How would you handle a remote command that takes a long time?"**
Avoid `.read()` which blocks until the command finishes and buffers all output in memory.
Instead, read stdout line by line as it arrives:

```python
stdin, stdout, stderr = client.exec_command("tail -f /var/log/app.log")
for line in stdout:
    # line arrives as each line is written — you see output in real time
    print(line.strip())
    if "ERROR" in line:
        break
```

For truly long-running commands, set a timeout on the channel:
`client.exec_command("long-command", timeout=300)`

**"When would you use Ansible instead?"**
paramiko for ad-hoc Python automation where you need the connection to be part of a larger
script. Ansible when you need idempotent, declarative configuration management across many
hosts — Ansible handles inventory, parallelism, retry, templating, and idempotency for you.
For one-off diagnostic scripts and programmatic automation, paramiko. For ongoing
configuration management, Ansible.

**"psutil in prod?"**
Lightweight polling for alerting sidecars, Kubernetes liveness and readiness scripts, or
pre-flight checks before deployments ("is there enough disk space and free RAM before I
start this migration?"). Because it reads from the kernel directly (not by running commands),
it's fast and has minimal overhead compared to spawning processes.
