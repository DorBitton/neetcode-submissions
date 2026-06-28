# Scripting Interview Scenarios

Realistic exercises you'll get in SRE/DevOps interviews. Each has:
- Problem statement (as the interviewer states it)
- Clarifying questions to ask
- Worked solution with inline commentary
- Follow-up questions the interviewer will ask

## Warm-up (HR / screening round)
| Scenario | Difficulty | Topics |
|---|---|---|
| [log-parser.md](log-parser.md) | Easy | file-io, regex, collections |
| [url-health-check.md](url-health-check.md) | Easy | requests, argparse, exit codes |
| [ec2-inventory.md](ec2-inventory.md) | Medium | boto3, pagination, CLI |
| [disk-alert.md](disk-alert.md) | Medium | subprocess, alerting, bash |

## Senior / technical round
| Scenario | Difficulty | Topics |
|---|---|---|
| [cost-anomaly.md](cost-anomaly.md) | Medium | boto3, Cost Explorer, statistics |
| [log-correlation.md](log-correlation.md) | Medium | structured logging, trace IDs, JSON |
| [drift-detection.md](drift-detection.md) | Medium | boto3, Terraform state, JSON diff |
| [secrets-rotation.md](secrets-rotation.md) | Hard | boto3, Kubernetes, health checks |
| [canary-rollback.md](canary-rollback.md) | Hard | bash, Prometheus, kubectl |
