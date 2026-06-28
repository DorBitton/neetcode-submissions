# subprocess — Running Shell Commands from Python

## What subprocess is

The `subprocess` module lets you run shell commands from inside Python, the same way you'd type them in a terminal. This is essential for SRE scripts that need to call `kubectl`, run system commands, restart services, check disk usage, or do anything else that already has a CLI tool.

Without `subprocess`, you'd have to reimplement every system tool in Python. With it, you just call the tool and work with the output.

---

## 1. subprocess.run — The Main Function You'll Use

`subprocess.run()` starts a process, waits for it to finish, and returns a result object. It's the right tool for 90% of use cases.

Before diving into code, understand each parameter — they're not optional details, they matter for correctness and security.

### The first argument: a LIST of strings, not a string

```python
subprocess.run(["ls", "-la", "/var/log"])
```

The command and every argument are **separate strings in a list**. This is deliberate.

When you pass a list, Python hands each element directly to the OS as a separate argument. The shell is never involved. There's no interpretation of special characters like `;`, `|`, `>`, or `$`.

When you pass a plain string (with `shell=True`), Python hands it to `/bin/sh` which then interprets every special character. This opens the door to shell injection attacks — covered in detail in section 3.

### All the parameters, explained

```python
import subprocess

result = subprocess.run(
    ["ls", "-la", "/var/log"],  # command + args as a list — each element is one argument
    capture_output=True,         # see below
    text=True,                   # see below
    check=True,                  # see below
    timeout=10                   # see below
)
```

**`capture_output=True`**

Without this, stdout and stderr from the command print directly to your terminal — you can't read them in Python. With `capture_output=True`, they're captured and stored in `result.stdout` and `result.stderr` so your script can inspect, parse, or log them.

Think of it like the difference between letting a command print to screen vs. saving its output to a variable.

**`text=True`**

By default, subprocess returns bytes (`b"some output\n"`). You'd have to decode them manually (`result.stdout.decode("utf-8")`). `text=True` does that automatically, giving you a normal Python string. Almost always what you want.

**`check=True`**

Every process exits with a return code. `0` means success. Anything else means failure — this is a Unix convention (you'll see `exit 0` at the end of bash scripts for the same reason).

Without `check=True`, if your command fails, Python just continues silently. `result.returncode` will be non-zero, but nothing blows up. You have to check it manually.

With `check=True`, a non-zero exit code raises `CalledProcessError` immediately. This is almost always what you want — fail loudly rather than silently proceeding on a broken result.

**`timeout=10`**

How many seconds to wait before giving up. Without a timeout, if the command hangs (e.g., a `kubectl` call to an unreachable cluster), your script hangs forever — which means the cron job or automation that called it also hangs forever. Always set a timeout.

---

## 2. The Result Object

After the command finishes, `subprocess.run()` returns a `CompletedProcess` object with everything you need.

```python
result = subprocess.run(
    ["kubectl", "get", "pods", "-n", "prod"],
    capture_output=True,
    text=True,
    timeout=15
)

# stdout — the normal output of the command, as a string (with text=True)
print(result.stdout)

# stderr — error messages and warnings the command wrote to stderr
print(result.stderr)

# returncode — the exit code: 0 = success, anything else = failure
print(result.returncode)

# Manual check when you didn't use check=True
# (useful when a non-zero code isn't always a hard error)
if result.returncode != 0:
    print(f"Command failed: {result.stderr}")
```

**Catching the exception when using check=True:**

```python
try:
    # "false" is a Unix command that immediately exits with code 1 — useful for testing
    subprocess.run(["false"], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(e.returncode)   # 1
    print(e.stderr)       # whatever the command wrote to stderr
    print(e.cmd)          # the command that failed, as a list
```

`CalledProcessError` carries `returncode`, `stdout`, `stderr`, and `cmd` — everything you need to log a useful error message.

---

## 3. shell=True vs List Args — Security Critical

This is the most important concept in subprocess. Get this wrong and you can introduce a critical security vulnerability.

### What shell=True actually does

When you write:

```python
subprocess.run("ls /var/log", shell=True)
```

Python hands that string to `/bin/sh -c 'ls /var/log'`. The shell then parses it exactly the way it would if you'd typed it in a terminal — which means it interprets `;`, `|`, `>`, `$(...)`, `&&`, etc.

### The attack

```python
# Imagine your script takes a filename from user input (command-line arg, API call, form, etc.)
user_input = "file.log; rm -rf /"

# DANGEROUS — don't do this
subprocess.run(f"grep {user_input}", shell=True)

# The shell sees this string:
#   grep file.log; rm -rf /
#
# The semicolon is a command separator. The shell runs:
#   1. grep file.log       <- harmless
#   2. rm -rf /            <- deletes everything on the system
#
# The attacker just got arbitrary command execution.
```

### The safe alternative

```python
# SAFE — always prefer this
subprocess.run(["grep", user_input, "file.log"])

# Python passes three arguments directly to grep:
#   argv[0] = "grep"
#   argv[1] = "file.log; rm -rf /"    <- the whole string is ONE argument
#   argv[2] = "file.log"
#
# The shell is never involved. grep looks for a pattern literally named
# "file.log; rm -rf /" — semicolons mean nothing to grep. Harmless.
```

### When shell=True is acceptable

Only for trusted, hardcoded commands where you need shell features (pipes, globs, variable expansion) and there is absolutely no user input involved:

```python
# OK — the entire string is hardcoded, nothing from user input
subprocess.run("ls /var/log | grep app-*.log", shell=True, text=True)
```

Even then, consider whether you can avoid it. For the above you could use Python's `glob` module instead.

**Rule of thumb:** if any part of the command string comes from outside your script — user input, environment variables, API responses, database values — never use `shell=True`.

---

## 4. Timeout Handling

```python
try:
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "prod"],
        capture_output=True,
        text=True,
        timeout=30    # wait at most 30 seconds
    )
except subprocess.TimeoutExpired as e:
    # e.timeout — how many seconds were allowed
    print(f"kubectl timed out after {e.timeout}s")

    # e.stdout and e.stderr contain whatever partial output arrived before the timeout.
    # IMPORTANT: these are bytes, not str, even if you set text=True.
    # This is a known quirk of subprocess — you have to decode manually here.
    if e.stdout:
        print("Partial output:", e.stdout.decode("utf-8", errors="replace"))
```

Why `TimeoutExpired` matters in SRE work: if you're running `kubectl` against a cluster with network issues, or `ssh` to an unreachable host, the command can hang indefinitely. Without a timeout, your monitoring script or cron job hangs with it, eventually piling up zombie processes. Always set a timeout.

---

## 5. Popen — When run() Isn't Enough

`subprocess.run()` waits for the command to finish and returns everything at once. Sometimes you need to process output **as it arrives** — for example:

- Tailing a log file in real time
- A long deploy script where you want to show progress
- Running a command that produces so much output it won't fit in memory

For those cases, use `Popen()`. It starts the process and gives you a file-like object you can read line by line.

```python
import subprocess

# Start the process — does NOT wait for it to finish
proc = subprocess.Popen(
    ["tail", "-f", "/var/log/app.log"],   # -f means "follow" — runs indefinitely
    stdout=subprocess.PIPE,                # PIPE means: capture stdout into a Python object
    stderr=subprocess.PIPE,
    text=True                              # decode each line to str automatically
)

try:
    # proc.stdout is a file-like object — iterating it blocks until each line arrives
    for line in proc.stdout:
        line = line.rstrip()          # remove trailing newline
        if "ERROR" in line:
            print(f"ALERT: {line}")
except KeyboardInterrupt:
    # User pressed Ctrl+C — cleanly stop the process
    proc.terminate()

# communicate() is the alternative for SHORT commands where you want all output at once
# It's like run() but on a Popen object you already started
stdout, stderr = proc.communicate(timeout=10)
```

`Popen` gives you fine-grained control — you can send input to the process, read from it incrementally, kill it, check if it's still alive, etc. The tradeoff is you're responsible for managing the process lifecycle.

---

## 6. shlex.split — Safely Convert a String to a List

Sometimes you have a command as a string (maybe read from a config file, or built programmatically) and need to convert it to a list for subprocess. Don't split on spaces — that breaks quoted arguments.

```python
import shlex

# BAD — splits on every space, breaks quoted args
cmd = 'grep -r "ERROR message" /var/log'
cmd.split()
# ['grep', '-r', '"ERROR', 'message"', '/var/log']   <-- WRONG
# grep would receive '"ERROR' and 'message"' as separate arguments

# GOOD — shlex.split handles quoting the same way a shell would
args = shlex.split(cmd)
# ['grep', '-r', 'ERROR message', '/var/log']   <-- correct
# 'ERROR message' (with the space) is preserved as one argument

subprocess.run(args, capture_output=True, text=True)

# Reverse: list → shell-safe string (useful for logging the command you're about to run)
shell_str = shlex.join(["kubectl", "get", "pods", "-n", "prod namespace"])
print(shell_str)   # "kubectl get pods -n 'prod namespace'"
# shlex.join adds quotes where necessary so the string is copy-pasteable into a terminal
```

---

## 7. Pipe Equivalent — Chaining Two Processes

In bash you'd write `ps aux | grep nginx`. In Python you chain two `Popen` calls, connecting the stdout of the first to the stdin of the second.

```python
import subprocess

# bash equivalent: ps aux | grep nginx
p1 = subprocess.Popen(
    ["ps", "aux"],
    stdout=subprocess.PIPE    # capture p1's stdout so we can pipe it
)

p2 = subprocess.Popen(
    ["grep", "nginx"],
    stdin=p1.stdout,           # feed p1's stdout into p2's stdin
    stdout=subprocess.PIPE,
    text=True
)

# This line is important: close our reference to p1.stdout.
# After this, p2 is the only thing reading p1's stdout.
# If p2 exits early (finds what it wants), p1 gets SIGPIPE and also exits.
# Without this close(), p1 would keep running even after p2 is done,
# because Python still holds the pipe open.
p1.stdout.close()

# Read all of p2's output and wait for it to finish
stdout, _ = p2.communicate()
print(stdout)
```

---

## 8. Common SRE Patterns

### Parse JSON output from kubectl

```python
import subprocess, json

result = subprocess.run(
    ["kubectl", "get", "pods", "-n", "prod", "-o", "json"],
    capture_output=True,
    text=True,
    check=True,
    timeout=15
)

# result.stdout is a JSON string — parse it into a Python dict
pods = json.loads(result.stdout)

for item in pods["items"]:
    name = item["metadata"]["name"]
    phase = item["status"]["phase"]
    print(f"{name}: {phase}")
```

### Run a command on a remote host

```python
result = subprocess.run(
    ["ssh", "-o", "StrictHostKeyChecking=no", "user@host", "uptime"],
    capture_output=True,
    text=True,
    timeout=10
    # Note: check=True omitted here — you might want to handle SSH failures differently
)

if result.returncode != 0:
    print(f"SSH failed: {result.stderr}")
else:
    print(result.stdout)
```

### Full example with error handling

```python
import subprocess

def run_kubectl(args: list[str], timeout: int = 30) -> str:
    """Run a kubectl command and return stdout. Raises on failure."""
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True,
            text=True,
            check=True,         # raise CalledProcessError on non-zero exit
            timeout=timeout
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"kubectl failed (exit {e.returncode}): {e.stderr}") from e
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"kubectl timed out after {timeout}s")

output = run_kubectl(["get", "pods", "-n", "prod"])
print(output)
```
