# Scripting Interview Questions

Organized by interview stage. HR/screening = basic Python and "have you done X". Technical = live coding or design.

---

## HR / Screening Round

These come up in the first 30-minute call. Expect "tell me about a time you..." or "have you used X?"

### Python Fundamentals
- **What's the difference between a list and a tuple?** → List is mutable, tuple is immutable. Tuples are hashable (can be dict keys or set members). Use tuple when data shouldn't change.
- **What does `*args` and `**kwargs` do?** → `*args` = positional args as tuple; `**kwargs` = keyword args as dict. Useful for passing unknown number of arguments.
- **How do you handle exceptions in Python?** → `try/except/else/finally`. `else` runs if no exception. `finally` always runs (cleanup). Re-raise with bare `raise` to preserve original traceback.
- **What's the difference between `except Exception` and `except BaseException`?** → `BaseException` catches SystemExit and KeyboardInterrupt too — almost never what you want. Use `Exception`.
- **What's a generator and when would you use one?** → Function with `yield`. Produces values lazily — doesn't load everything into memory. Use when iterating over large datasets (log files, DB rows).
- **What's the GIL and how does it affect threading?** → Global Interpreter Lock — only one thread runs Python bytecode at a time. For I/O-bound tasks (HTTP calls, file reads) threading still works because GIL releases during I/O. For CPU-bound tasks, use `multiprocessing`.
- **When do you use threading vs multiprocessing vs asyncio?** → Threading: I/O-bound, simple. Multiprocessing: CPU-bound. Asyncio: I/O-bound, many concurrent connections, higher efficiency than threads at scale.
- **What's a mutable default argument gotcha?** → `def fn(lst=[]):` — the list is created once and shared across calls. Use `def fn(lst=None): lst = lst or []` instead.

### Scripting Experience
- **Have you written Python scripts for automation?** → Reference scenarios: log parsing, URL health check, EC2 inventory (see `scenarios/`)
- **Have you used boto3?** → Yes — EC2 describe/filter, S3 list/get/put, SSM Parameter Store, paginators for >1000 results
- **Have you used subprocess?** → Yes — running kubectl/shell commands from Python safely using list args (not shell=True) to avoid injection
- **Have you used paramiko?** → Yes — SSH into remote servers from Python to run commands or collect health data without leaving the script
- **How do you keep secrets out of scripts?** → Environment variables (`os.environ["DB_PASS"]`), AWS SSM Parameter Store with `WithDecryption=True`, never hardcode credentials

---

## Technical / Live Coding Round

Expect: "write a script that does X" or "how would you approach Y"

### File and Log Processing
- **Parse a log file and count 500 errors per minute** → Stream with `for line in f` (never readlines), regex for timestamp + status, defaultdict(int) for counts → see `scenarios/log-parser.md`
- **Find all files modified in the last 24 hours** → `pathlib.Path('.').rglob('*')`, filter by `.stat().st_mtime > time.time() - 86400`
- **How do you read a large file without running out of memory?** → Stream line by line: `for line in open(path)`. Never `.read()` or `.readlines()` on unknown-size files.

### System / Subprocess
- **Write a script to restart a service if its health endpoint returns non-200** → `requests.get(url, timeout=5)`, check `r.status_code`, `subprocess.run(["systemctl", "restart", "svc"], check=True)`
- **How do you safely run shell commands from Python?** → `subprocess.run(["cmd", "arg1", "arg2"], ...)` — list args, not string + `shell=True`. String + shell=True is injection risk with user input.
- **How would you tail a log file and alert on a pattern?** → `subprocess.Popen(["tail", "-f", path], stdout=PIPE)`, iterate stdout lines, check pattern, POST to Slack webhook

### AWS / Boto3
- **List all S3 buckets and their total sizes** → `s3.list_buckets()`, then for each bucket use `s3.get_paginator("list_objects_v2")`, sum `obj["Size"]`
- **Find EC2 instances with no Name tag** → describe_instances paginator, for each instance check `i.get("Tags")` — if no tag with Key=="Name", flag it
- **Read a secret from SSM Parameter Store** → `ssm.get_parameter(Name="/path", WithDecryption=True)["Parameter"]["Value"]`
- **Why do you need paginators in boto3?** → API truncates results at 1000. Without paginator you silently miss resources.

### Bash
- **What does `set -euo pipefail` do?** → `-e`: exit on error. `-u`: error on unset variable. `-o pipefail`: pipe fails if any command in it fails (not just last).
- **How do you parse the 5th column of a file?** → `awk '{print $5}' file` or `cut -d' ' -f5 file`
- **How do you find the top 10 most frequent IPs in an nginx log?** → `awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10`

---

## Design / Senior Round

Expect open-ended questions about reliability, automation, and operational thinking.

- **"How would you write a deployment script that's safe to re-run?"** → Idempotency: check current state before making changes. `if instance_exists(): update() else: create()`. Never assume starting state.
- **"How would you handle a script that runs in CI and needs AWS credentials?"** → IAM role for CI (GitHub Actions OIDC, Jenkins IAM role) — never put access keys in env vars or code. Role assumed automatically.
- **"Your script works locally but fails in production — how do you debug it?"** → Add `--dry-run` flag, add verbose logging (`-v`), print env at startup, check IAM permissions (AccessDenied?), check network (can prod reach the endpoint?).
- **"How do you make a script observable?"** → Structured JSON logging, explicit exit codes, print summary at end, write metrics to CloudWatch/Prometheus if long-running.
- **"Walk me through how you'd detect infrastructure drift"** → Compare Terraform state file against live AWS API. Flag resources in AWS not in state (manual additions) and resources in state not in AWS (manual deletions). → see `scenarios/drift-detection.md`
- **"You rotate a secret and pods look healthy but users can't connect — what happened?"** → Connection pool uses stale credentials. Readiness probe checked /healthz (HTTP alive), not /healthz/db (DB auth). → see `scenarios/secrets-rotation.md`
- **"Your canary has 0% errors but users are complaining. Why didn't your automation roll it back?"** → Automation watched error rate only. Canary is slow (high P99 latency) but returns 200. Fix: watch both error rate AND latency. → see `scenarios/canary-rollback.md`
