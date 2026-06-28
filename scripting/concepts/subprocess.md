# subprocess — SRE Reference

## 1. subprocess.run — Basic Invocation

```python
import subprocess

result = subprocess.run(
    ["ls", "-la", "/var/log"],
    capture_output=True,    # capture stdout + stderr
    text=True,              # decode bytes → str
    check=True,             # raise CalledProcessError on non-zero exit
    timeout=10              # raise TimeoutExpired after 10s
)
```

---

## 2. Result Object

```python
result.stdout           # string (with text=True)
result.stderr           # string
result.returncode       # int — 0 = success

# Without check=True — manual check
if result.returncode != 0:
    print(f"Failed: {result.stderr}")

# CalledProcessError contains output too
try:
    subprocess.run(["false"], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(e.returncode)     # 1
    print(e.stderr)         # captured stderr
```

---

## 3. shell=True vs List Args

```python
# List args — PREFERRED — no shell injection risk
subprocess.run(["grep", "-r", "ERROR", "/var/log"], capture_output=True, text=True)

# shell=True — string passed to /bin/sh
# OK for trusted, hardcoded commands with shell features (pipes, globs)
subprocess.run("ls /var/log | grep app", shell=True, text=True)

# NEVER with user input
user_input = "file.log; rm -rf /"
subprocess.run(f"grep {user_input}", shell=True)   # INJECTION — don't do this

# If you need shell features + dynamic args, build the list manually:
subprocess.run(["grep", "-r", user_input, "/var/log"], capture_output=True, text=True)
```

---

## 4. Timeout

```python
try:
    result = subprocess.run(
        ["kubectl", "get", "pods"],
        capture_output=True, text=True,
        timeout=30              # seconds
    )
except subprocess.TimeoutExpired as e:
    print(f"Command timed out after {e.timeout}s")
    # e.stdout / e.stderr contain partial output (bytes)
```

---

## 5. Popen — Streaming Output

```python
import subprocess

# Stream output line by line — good for long-running commands
proc = subprocess.Popen(
    ["tail", "-f", "/var/log/app.log"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

try:
    for line in proc.stdout:        # blocks until line available
        line = line.rstrip()
        if "ERROR" in line:
            print(f"ALERT: {line}")
except KeyboardInterrupt:
    proc.terminate()

# communicate() — for short commands, reads all output at once
stdout, stderr = proc.communicate(timeout=10)
```

---

## 6. shlex.split

```python
import shlex

# Convert shell string → list safely (handles quoting)
cmd = 'grep -r "ERROR message" /var/log'
args = shlex.split(cmd)
# ['grep', '-r', 'ERROR message', '/var/log']

subprocess.run(args, capture_output=True, text=True)

# Reverse — list → shell-safe string (for logging)
shell_str = shlex.join(["kubectl", "get", "pods", "-n", "prod"])
print(shell_str)   # "kubectl get pods -n prod"
```

---

## 7. Common SRE Patterns

```python
import subprocess, shlex

# Safe invocation
result = subprocess.run(
    ["kubectl", "get", "pods", "-n", "prod"],
    capture_output=True, text=True, check=True, timeout=10
)
print(result.stdout)

# Stream long output
proc = subprocess.Popen(["tail", "-f", "/var/log/app.log"], stdout=subprocess.PIPE, text=True)
for line in proc.stdout:
    if "ERROR" in line:
        print(f"ALERT: {line}")

# Never do this with user input:
# subprocess.run(f"grep {user_input} file.log", shell=True)  # injection risk
```

```python
# Get kubectl output as dict
import json

result = subprocess.run(
    ["kubectl", "get", "pods", "-n", "prod", "-o", "json"],
    capture_output=True, text=True, check=True, timeout=15
)
pods = json.loads(result.stdout)
for item in pods["items"]:
    print(item["metadata"]["name"], item["status"]["phase"])

# Run script on remote host
result = subprocess.run(
    ["ssh", "-o", "StrictHostKeyChecking=no", "user@host", "uptime"],
    capture_output=True, text=True, timeout=10
)

# Pipe equivalent — chain two processes
p1 = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "nginx"], stdin=p1.stdout,
                       stdout=subprocess.PIPE, text=True)
p1.stdout.close()                       # allow p1 to receive SIGPIPE if p2 exits
stdout, _ = p2.communicate()
```
