# Python Scripting for SRE

Python as a tool for automation, not interview problems. The scripts you'll actually write on the job.

---

## Planned Topics

| File | What's in it | Status |
|---|---|---|
| `concepts/file-io.md` | Reading logs, parsing files, writing reports | ⬜ |
| `concepts/subprocess.md` | Running shell commands from Python | ⬜ |
| `concepts/requests.md` | HTTP calls to APIs, webhooks | ⬜ |
| `concepts/boto3.md` | AWS SDK — list EC2, S3, describe infra | ⬜ |
| `concepts/cli-tools.md` | argparse, click — writing proper CLI scripts | ⬜ |
| `interview-questions.md` | Live coding questions SREs get asked | ⬜ |

---

## What interview questions look like for scripting

- Parse this log file and count how many 500 errors occurred per minute
- Write a script that checks if a list of URLs are reachable
- Use boto3 to list all EC2 instances and their state across regions
- Write a health check that alerts if a service is down
