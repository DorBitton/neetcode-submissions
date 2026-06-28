# File I/O — SRE Reference

## 1. `with open()` Patterns

```python
# Modes: r (read), w (write/truncate), a (append), rb/wb (binary)
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()              # full string

with open("out.txt", "w", encoding="utf-8") as f:
    f.write("line\n")

with open("log.txt", "a", encoding="utf-8") as f:
    f.write("appended line\n")

with open("image.png", "rb") as f:
    data = f.read()                 # bytes
```

---

## 2. pathlib

```python
from pathlib import Path

p = Path("/var/log/app")

p.exists()                          # True/False
p.is_file() / p.is_dir()
p.read_text(encoding="utf-8")       # returns string
p.write_text("content", encoding="utf-8")

# Navigation
log_dir = Path("/var/log")
app_log = log_dir / "app" / "app.log"   # / operator joins paths
app_log.parent                           # /var/log/app
app_log.name                             # "app.log"
app_log.stem                             # "app"
app_log.suffix                           # ".log"

# Glob / iterate
for f in Path("/etc").glob("*.conf"):    # flat
    print(f)
for f in Path("/etc").rglob("*.conf"):   # recursive
    print(f)
for entry in Path("/var/log").iterdir(): # list dir entries
    print(entry)
```

---

## 3. Line-by-Line Log Parsing

```python
# Parse log file, count 500s per minute
from collections import defaultdict
import re

counts = defaultdict(int)
pattern = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*\s500\s')

with open('access.log') as f:
    for line in f:          # streams — doesn't load full file
        m = pattern.search(line)
        if m:
            counts[m.group(1)] += 1

for minute, count in sorted(counts.items()):
    print(f"{minute}  {count} errors")
```

---

## 4. CSV

```python
import csv

# Read — row as list
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)                        # skip header
    for row in reader:
        print(row[0], row[1])

# Read — row as dict (header keys)
with open("data.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["hostname"], row["ip"])

# Write
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["hostname", "ip"])         # header
    writer.writerows([["web01", "10.0.0.1"],
                      ["web02", "10.0.0.2"]])
```

---

## 5. JSON

```python
import json

# Load from file
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)               # dict/list

# Dump to string
output = json.dumps(config, indent=2)   # pretty-print
json.dumps(config, sort_keys=True)

# Dump to file
with open("out.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

# Handle parse errors
try:
    data = json.loads(raw_string)
except json.JSONDecodeError as e:
    print(f"Bad JSON at line {e.lineno}: {e.msg}")

# Parse API response body
import requests
r = requests.get("https://api.example.com/data")
data = r.json()                         # shorthand for json.loads(r.text)
```

---

## 6. YAML

```python
# pip install pyyaml
import yaml

# Load
with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)          # safe_load — no arbitrary code exec

# Load string
config = yaml.safe_load("key: value\nlist:\n  - a\n  - b")

# Dump
print(yaml.dump(config, default_flow_style=False))  # block style

# GOTCHA: never use yaml.load() — use yaml.safe_load()
#         yaml.load() can execute arbitrary Python via !!python/object
```

---

## 7. Temp Files

```python
import tempfile
import os

# Temp file — auto-deleted on close (delete=True by default)
with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                  delete=False, encoding="utf-8") as f:
    f.write('{"key": "value"}')
    tmp_path = f.name               # get path before close

# Use file...
os.unlink(tmp_path)                 # manual cleanup when delete=False

# Temp directory — you manage cleanup
tmp_dir = tempfile.mkdtemp()        # returns path string
# ... write files into tmp_dir ...
import shutil
shutil.rmtree(tmp_dir)              # cleanup

# Context manager for temp dir (auto-cleanup)
with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_file = os.path.join(tmp_dir, "work.txt")
    Path(tmp_file).write_text("data")
    # deleted when block exits
```
