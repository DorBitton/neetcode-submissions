# Scenario: Log Parser

**Difficulty:** Easy
**Topics:** file-io, regex, collections

---

## Problem Statement

> "Given an nginx access log, write a script that counts how many 500-level errors occurred per minute and prints them sorted by time."

---

## Clarifying Questions to Ask

- What is the log format? (combined, custom, JSON?)
- Should I accept the path as an argument or can it be hardcoded?
- Output to stdout or a file?
- Should the script exit 1 if errors are found (for use in alerting pipelines)?
- Should I skip lines that don't match the pattern or fail loudly?

---

## Worked Solution

```python
#!/usr/bin/env python3
import argparse, re, sys
from collections import defaultdict

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("logfile", help="Path to nginx access log")
    p.add_argument("--threshold", type=int, default=0,
                   help="Exit 1 if any minute exceeds this count")
    return p.parse_args()

def count_500s_per_minute(path):
    # Regex matches "2024-01-15 14:23" prefix and 5xx status code
    # Using search() not match() — the timestamp isn't at line start in combined format
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*\s5\d\d\s')
    counts = defaultdict(int)
    with open(path) as f:
        for line in f:              # stream — don't load 100GB into memory
            m = pattern.search(line)
            if m:
                counts[m.group(1)] += 1
    return counts

def main():
    args = parse_args()
    counts = count_500s_per_minute(args.logfile)
    if not counts:
        print("No 5xx errors found.")
        return
    breached = False
    for minute, count in sorted(counts.items()):   # sorted() on ISO timestamps = chronological order
        print(f"{minute}  {count} errors")
        if args.threshold and count > args.threshold:
            breached = True
    if breached:
        # Write alert to stderr so stdout stays machine-parseable
        print(f"ALERT: threshold of {args.threshold} exceeded", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Bash one-liner alternative

```bash
grep ' 5[0-9][0-9] ' access.log | awk '{print substr($4,2,16)}' | cut -c1-16 | sort | uniq -c | sort -k2
```

Show this if asked "how would you do this without Python." Demonstrates you know both.

---

## Follow-up Questions the Interviewer Will Ask

**"What if the file is 100GB?"**
Already handled — streaming line by line with `for line in f`. Never loads the full file. Using `readlines()` or `f.read()` would OOM the process.

**"How would you run this every 5 minutes?"**
Cron:
```
*/5 * * * * /usr/local/bin/check-errors.py /var/log/nginx/access.log --threshold 10
```
For better observability, redirect stderr to a log file and stdout to `/dev/null`.

**"How would you alert to Slack?"**
POST to a Slack webhook URL:
```python
import requests
requests.post(SLACK_WEBHOOK_URL, json={"text": f"ALERT: {count} 5xx errors at {minute}"})
```

**"What if the log format is JSON?"**
Replace the regex with `json.loads(line)` and key lookup — more robust than regex parsing.

**"How would you test this?"**
Write a small test log file with known contents, assert the output counts match expectations. Can use `unittest` or `pytest` with a `tmp_path` fixture.
