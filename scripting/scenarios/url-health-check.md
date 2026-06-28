# Scenario: URL Health Check

**Difficulty:** Easy
**Topics:** requests, argparse, exit codes, concurrency

---

## Problem Statement

> "Write a script that takes a list of URLs from a file and checks if each returns HTTP 200. Print a summary and exit 1 if any are down."

---

## Clarifying Questions to Ask

- What timeout per request is acceptable?
- Should I retry on transient failure, or fail immediately?
- Sequential or concurrent? (important if there are hundreds of URLs)
- What counts as "down" — connection failure only, or also 4xx/5xx?
- Output format: human-readable or structured (JSON/CSV) for downstream tooling?

---

## Worked Solution — Sequential (start here)

```python
#!/usr/bin/env python3
import argparse, sys
import requests

def check_url(url, timeout):
    try:
        r = requests.get(url, timeout=timeout)
        # Treat anything other than 200 as down — adjust if 3xx redirects should count
        return r.status_code == 200, r.status_code
    except requests.exceptions.Timeout:
        return False, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return False, "CONNECTION_ERROR"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("urlfile", help="File with one URL per line")
    p.add_argument("--timeout", type=int, default=5)
    args = p.parse_args()

    with open(args.urlfile) as f:
        # Strip whitespace, skip blank lines
        urls = [line.strip() for line in f if line.strip()]

    results = []
    for url in urls:
        ok, status = check_url(url, args.timeout)
        results.append((url, ok, status))
        print(f"{'OK' if ok else 'DOWN':4}  {status}  {url}")

    down = [r for r in results if not r[1]]
    print(f"\n{len(urls)} checked, {len(down)} down")
    if down:
        sys.exit(1)   # non-zero exit for use in CI / alerting pipelines

if __name__ == "__main__":
    main()
```

---

## Concurrent Version (for many URLs)

Mention this when the interviewer asks "what if you have 100 URLs?" Show you know when sequential becomes a bottleneck.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(check_url, url, args.timeout): url for url in urls}
    for future in as_completed(futures):
        url = futures[future]
        ok, status = future.result()
        print(f"{'OK' if ok else 'DOWN':4}  {status}  {url}")
```

- `max_workers=10` — enough parallelism without hammering targets or exhausting file descriptors
- `as_completed` — print results as they arrive, no waiting for slowest URL before printing faster ones
- The dict `{future: url}` pattern is idiomatic for mapping futures back to their inputs

---

## Follow-up Questions the Interviewer Will Ask

**"How would you schedule this every 5 minutes?"**
Cron or a systemd timer. cron is simpler; systemd timer is better for logging and dependency control.

**"What if you have 10,000 URLs?"**
Switch to `asyncio` + `aiohttp`. Threads have ~1MB stack overhead each — you cannot spin up 10,000 threads. `asyncio` handles thousands of concurrent I/O ops from a single thread with an event loop.

```python
import asyncio, aiohttp

async def check(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as r:
            return url, r.status == 200, r.status
    except Exception as e:
        return url, False, str(e)

async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [check(session, u) for u in urls]
        return await asyncio.gather(*tasks)
```

**"What's the difference between threading and asyncio here?"**
Both are I/O-bound, so both avoid the GIL problem. Threading is simpler and good enough for ~100-200 URLs. asyncio is more efficient at scale (no thread-per-request overhead) but requires async-aware libraries everywhere.

**"How would you add retry logic?"**
Use `tenacity` or a manual loop with exponential backoff:
```python
for attempt in range(3):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200, r.status_code
    except requests.exceptions.Timeout:
        if attempt == 2:
            return False, "TIMEOUT"
        time.sleep(2 ** attempt)
```
