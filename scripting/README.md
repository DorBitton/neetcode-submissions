# Python Scripting for SRE

Python and bash as tools for automation — not interview puzzles, but the scripts you'll actually write on the job.

---

## How to use this

**Stuck on syntax mid-interview?** → Open a file in `concepts/`

**Preparing for an interview?** → Work through `scenarios/` — each has the problem statement, a worked solution, and the follow-up questions you'll get

**Question bank** → `interview-questions.md` — organized by interview stage

---

## Concepts — syntax reference

| File | What's in it |
|---|---|
| `concepts/python-basics.md` | Variables, control flow, functions, error handling, strings, data structures |
| `concepts/file-io.md` | Log parsing, CSV, JSON, YAML, pathlib, temp files |
| `concepts/subprocess.md` | Running shell commands safely from Python, streaming output |
| `concepts/requests.md` | HTTP calls, retries, sessions, pagination |
| `concepts/boto3.md` | AWS SDK — EC2, S3, SSM, paginators, error handling |
| `concepts/cli-tools.md` | argparse, click, logging, exit codes |
| `concepts/bash-essentials.md` | set -euo pipefail, traps, awk/sed one-liners |
| `concepts/paramiko-psutil.md` | SSH from Python, system monitoring |

---

## Scenarios — interview exercises

### Warm-up (HR / screening round)
| Scenario | Topics |
|---|---|
| `scenarios/log-parser.md` | file-io, regex, streaming large files |
| `scenarios/url-health-check.md` | requests, threading, exit codes |
| `scenarios/ec2-inventory.md` | boto3, pagination, CSV output |
| `scenarios/disk-alert.md` | bash df parsing, psutil, alerting |

### Senior / technical round
| Scenario | Topics |
|---|---|
| `scenarios/cost-anomaly.md` | Cost Explorer, statistical baseline, billing attribution |
| `scenarios/log-correlation.md` | Trace IDs, structured logging, invisible failures |
| `scenarios/drift-detection.md` | Terraform state diff, blind spots |
| `scenarios/secrets-rotation.md` | K8s readiness probe gap, /healthz vs /healthz/db |
| `scenarios/canary-rollback.md` | Error rate vs P99 latency, bash + Prometheus |

---

## Key libraries

| Library | Use |
|---|---|
| `boto3` | AWS SDK |
| `requests` | HTTP calls |
| `subprocess` | Shell commands from Python |
| `paramiko` | SSH remote execution |
| `psutil` | System monitoring (CPU, memory, disk) |
| `pathlib` | File system operations |
| `argparse` / `click` | CLI tools |

---

## What interview questions look like

- Parse this log file and count how many 500 errors occurred per minute
- Write a script that checks if a list of URLs are reachable
- Use boto3 to list all EC2 instances and their state across regions
- Your canary has zero errors but users are slow — why didn't the automation roll it back?
- You rotated a secret and pods look healthy but users can't connect — what happened?

See `interview-questions.md` for the full bank with answer notes.
