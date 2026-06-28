# Scenario: Disk Alert

**Difficulty:** Medium
**Topics:** bash, subprocess, alerting, psutil

---

## Problem Statement

> "Write a bash script that checks disk usage on all mount points and sends an alert if any exceeds 80%."

---

## Clarifying Questions to Ask

- Which mount points should I skip? (tmpfs, devtmpfs, loop devices?)
- Alert destination: stderr + exit 1, or push to Slack/PagerDuty?
- Is the threshold configurable or hardcoded?
- Will this run as a cron job or a daemon?
- Should it alert once per breach or suppress duplicates?

---

## Worked Solution — Bash

```bash
#!/usr/bin/env bash
set -euo pipefail
# set -e: exit on error; set -u: fail on unset vars; set -o pipefail: catch pipe failures

THRESHOLD="${THRESHOLD:-80}"   # configurable via env var, default 80
ALERT=0

# df -P: POSIX portable output (no line-wrapping, consistent columns)
# tail -n +2: skip the header line
# grep -v: exclude pseudo-filesystems that will always look "full"
while IFS= read -r line; do
    usage=$(echo "$line" | awk '{print $5}' | tr -d '%')
    mount=$(echo "$line" | awk '{print $6}')
    if [[ "$usage" -ge "$THRESHOLD" ]]; then
        echo "ALERT: $mount is ${usage}% full (threshold: ${THRESHOLD}%)" >&2
        ALERT=1
    fi
done < <(df -P | tail -n +2 | grep -v '^tmpfs\|^devtmpfs')

exit "$ALERT"   # 0 = all clear, 1 = at least one breach
```

Key choices:
- `>&2` sends alerts to stderr so stdout stays clean for log pipelines
- `exit "$ALERT"` rather than `exit 1` inside the loop — checks all mounts, not just the first breach
- `THRESHOLD` as env var means no need to edit the script for different environments

---

## Python Alternative (psutil)

Show this if asked "how would you write this in Python?" or "what if you need to unit test it?"

```python
#!/usr/bin/env python3
import psutil, sys

THRESHOLD = 80
alert = False

for part in psutil.disk_partitions():
    # Skip loop devices (snaps) and pseudo-filesystems
    if "loop" in part.device or part.fstype in ("tmpfs", "devtmpfs", "squashfs"):
        continue
    try:
        usage = psutil.disk_usage(part.mountpoint)
    except PermissionError:
        continue    # some mount points are inaccessible to non-root
    if usage.percent >= THRESHOLD:
        print(f"ALERT: {part.mountpoint} is {usage.percent:.1f}% full", file=sys.stderr)
        alert = True

sys.exit(1 if alert else 0)
```

---

## Sending a Slack Alert

```bash
# From bash — add after setting ALERT=1
curl -s -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"DISK ALERT: $mount is ${usage}% full on $(hostname)\"}" \
  "$SLACK_WEBHOOK_URL"
```

```python
# From Python
import requests
requests.post(SLACK_WEBHOOK_URL, json={
    "text": f"DISK ALERT: {part.mountpoint} is {usage.percent:.1f}% full on {socket.gethostname()}"
})
```

---

## Follow-up Questions the Interviewer Will Ask

**"How would you deploy this as a cronjob?"**
```
*/15 * * * * /usr/local/bin/disk-alert.sh 2>>/var/log/disk-alert.log
```
Redirect stderr to a log file so alerts are visible after the fact, not just in cron's email output.

**"What's the difference between your bash and Python versions?"**
- Bash: zero dependencies, works on any system with `df`. Harder to unit test.
- Python (psutil): cross-platform, easier to unit test (mock psutil), more readable. Requires psutil installed (`pip install psutil`).
- For a simple disk check, bash is fine. For something that needs retries, structured output, or Slack integration, Python scales better.

**"How would you prevent alert spam if disk stays above threshold for hours?"**
State file approach — write the alerted mount points to `/tmp/disk-alert-state`. Only alert when a mount point transitions from OK to breached, not on every run:
```bash
STATE_FILE="/tmp/disk-alert.state"
touch "$STATE_FILE"
if ! grep -q "$mount" "$STATE_FILE"; then
    echo "ALERT: $mount" >&2
    echo "$mount" >> "$STATE_FILE"
fi
# Clear state file when mount drops below threshold
```

**"How would you test this?"**
Create a ramdisk or small loopback device, fill it to >80%, run the script, assert exit code is 1 and output contains the mount point.
