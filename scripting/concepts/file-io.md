# File I/O — SRE / DevOps Tutor Reference

This file is written as a tutor. Every section explains **what the thing is and why you need it** before showing code, and every non-obvious line has a comment. File I/O is one of the most common tasks in SRE scripts — parsing logs, reading configs, writing reports.

---

## 1. `open()` and `with`

`open()` is Python's built-in for opening files. The **`with` statement** is the correct way to use it. Here's why: `with` is a *context manager* — it guarantees that the file is closed when you leave the block, even if an exception is raised inside. Without `with`, you'd need to call `f.close()` manually. If your code crashes before it reaches `f.close()`, the file handle stays open — you "leak" a file descriptor. On a long-running server script, leaked file descriptors accumulate and eventually the OS refuses to open any more files.

The mode string controls what you can do with the file:
- `"r"` — read-only (default, file must exist)
- `"w"` — write (creates the file if it doesn't exist, **silently overwrites** if it does — be careful)
- `"a"` — append (creates if doesn't exist, adds to the end if it does — safe for logs)
- `"rb"` / `"wb"` — read/write binary (for images, zips, any non-text file)

```python
# --- Reading a file ---
# encoding="utf-8" is best practice — always be explicit about encoding
# without it, Python uses the system default which varies by OS
with open("config.txt", "r", encoding="utf-8") as f:
    content = f.read()           # reads the ENTIRE file into a single string
                                  # only safe for small files — see section 3 for large files

# Reading line by line (still loads all lines into memory as a list)
with open("config.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()        # returns a list of strings, each ending with "\n"

# --- Writing a file ---
# "w" mode creates the file if it doesn't exist.
# If the file ALREADY EXISTS, "w" OVERWRITES it completely with no warning.
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")      # you must include \n yourself — write() doesn't add it
    f.write("second line\n")

# --- Appending to a file ---
# "a" mode is safe for logs — it never destroys existing content
with open("app.log", "a", encoding="utf-8") as f:
    f.write("2024-01-15 service restarted\n")   # adds to the END of the file

# --- Reading binary files ---
# Use "rb" for anything that isn't plain text: images, zip archives, compiled files
with open("image.png", "rb") as f:
    data = f.read()              # data is a bytes object, not a string
    print(type(data))            # <class 'bytes'>
    print(data[:4])              # first 4 bytes — PNG files start with b'\x89PNG'

# --- Writing binary files ---
with open("copy.png", "wb") as f:
    f.write(data)                # write the bytes back out

# The with block automatically closes the file here — even if an exception occurred above
```

> **Common mistake:** Using `"w"` mode when you mean `"a"`. If you're writing a script that runs on a schedule and appends to a log file, using `"w"` will destroy the previous log on each run. Always double-check the mode when writing to files that already exist.

---

## 2. pathlib

`pathlib` is the **modern way to work with file paths** in Python (added in Python 3.4, now standard). Before pathlib, you'd use `os.path.join("var", "log", "app.log")` which gets verbose and error-prone. pathlib represents paths as objects, not strings, and gives them useful built-in methods.

The standout feature is the `/` operator for path concatenation. `Path("/var/log") / "app" / "app.log"` is more readable than string concatenation and handles OS-specific separators automatically (forward slash on Linux/Mac, backslash on Windows).

```python
from pathlib import Path

# --- Creating a Path object ---
# Path objects are not just strings — they have methods for common operations
p = Path("/var/log/app/app.log")

# --- Checking existence and type ---
p.exists()                              # True if the path exists at all (file or dir)
p.is_file()                            # True if it exists AND is a regular file
p.is_dir()                             # True if it exists AND is a directory

# --- Reading and writing (small files only) ---
# These are convenience methods — they open, read/write, and close in one call
text = p.read_text(encoding="utf-8")   # equivalent to open(p) + f.read()
p.write_text("new content", encoding="utf-8")  # equivalent to open(p, "w") + f.write()
raw_bytes = p.read_bytes()             # equivalent to open(p, "rb") + f.read()

# --- Path concatenation with the / operator ---
# This is the big win over os.path — readable and composable
log_dir = Path("/var/log")
app_log = log_dir / "app" / "app.log"   # produces Path("/var/log/app/app.log")
# Compare to the old way: os.path.join("/var/log", "app", "app.log")

# --- Inspecting parts of a path ---
p = Path("/var/log/app/app.log")
p.parent        # Path("/var/log/app") — the directory containing this file
p.name          # "app.log"            — the filename with extension
p.stem          # "app"                — the filename WITHOUT extension
p.suffix        # ".log"               — just the extension
p.parts         # ("/", "var", "log", "app", "app.log") — tuple of all parts

# Building a sibling path (file in the same directory with a different name)
backup = p.with_suffix(".bak")          # Path("/var/log/app/app.bak")
dated = p.with_name("app-2024.log")    # Path("/var/log/app/app-2024.log")

# --- Creating directories ---
Path("/tmp/myapp/data").mkdir(parents=True, exist_ok=True)
# parents=True: creates any missing parent directories (like mkdir -p)
# exist_ok=True: don't raise an error if the directory already exists

# --- Glob: find files matching a pattern ---
# glob() matches files in THIS directory only — not in subdirectories
for conf_file in Path("/etc").glob("*.conf"):
    print(conf_file)    # /etc/resolv.conf, /etc/nsswitch.conf, etc.

# rglob() (recursive glob) searches all subdirectories too
# "r" stands for recursive — equivalent to glob("**/*.conf")
for log_file in Path("/var/log").rglob("*.log"):
    print(log_file)     # finds .log files anywhere under /var/log

# --- iterdir(): list contents of a directory ---
for entry in Path("/var/log").iterdir():
    if entry.is_file():
        print(f"file: {entry.name}")
    elif entry.is_dir():
        print(f"dir:  {entry.name}")

# --- Using Path with open() ---
# Path objects work directly with open() — no need to convert to string
with open(app_log, "r", encoding="utf-8") as f:
    content = f.read()
```

> **Common mistake:** Forgetting that `Path / "subdir"` only works when the left side is already a `Path` object. `"/var/log" / "app"` raises `TypeError` because `/` between two strings is not defined. Always start with `Path(...)` on the left side.

---

## 3. Line-by-Line Log Parsing

When parsing log files, **never use `f.read()` or `f.readlines()` on large files**. Both methods load the entire file into memory at once. A 10 GB log file would require 10 GB of RAM. Instead, iterate the file object directly with `for line in f:` — this reads one line at a time from disk (buffered), so memory usage stays near-constant regardless of file size.

This pattern — open file, loop line by line, apply a regex, accumulate results in a `defaultdict` — is the foundation of most log analysis scripts you'll write as an SRE.

```python
from collections import defaultdict
import re

# --- Count HTTP 500 errors per minute from an access log ---
# Example log line: "2024-01-15 12:03:45 GET /api/users 500"

# Pre-compiling the regex is more efficient when you're matching thousands of lines.
# re.compile() builds the pattern object once; calling .search() on it is faster
# than re.search(pattern_string, line) which recompiles on every call.
pattern = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})'   # group 1: date + hour:minute (e.g. "2024-01-15 12:03")
    r'.*'                                   # .* matches anything in between (the method and path)
    r'\s500\s'                              # \s matches whitespace; 500 is the status code
                                            # \s on both sides avoids matching "1500" or "5001"
)

# defaultdict(int) means: if you access a key that doesn't exist,
# automatically create it with value 0 (the result of calling int()).
# This saves you from writing: if minute not in counts: counts[minute] = 0
counts = defaultdict(int)

with open("access.log", "r", encoding="utf-8") as f:
    for line in f:                          # reads ONE line at a time — memory efficient
        line = line.rstrip("\n")            # remove the trailing newline character
        m = pattern.search(line)            # search() finds the pattern anywhere in the line
        if m:                               # m is None if no match — always check
            minute = m.group(1)             # extract the captured group: "2024-01-15 12:03"
            counts[minute] += 1             # increment; defaultdict creates it at 0 if needed

# Print results sorted by time
for minute, count in sorted(counts.items()):   # sorted() on a dict iterates over sorted keys
    print(f"{minute}  {count} errors")

# --- Filtering and extracting fields from structured logs ---
# Example: "2024-01-15 12:03:45 web01 ERROR disk usage at 95%"
field_pattern = re.compile(r'^(\S+)\s(\S+)\s(\S+)\s(\w+)\s(.+)$')
# ^ = start of line, $ = end of line
# \S+ = one or more non-whitespace characters
# \w+ = one or more word characters (letters, digits, underscore)
# .+ = one or more of any character

with open("app.log", "r", encoding="utf-8") as f:
    for line in f:
        m = field_pattern.match(line)       # .match() anchors at the START of the string
        if m:
            date, time, host, level, msg = m.groups()   # .groups() returns all captured groups
            if level == "ERROR":
                print(f"[{host}] {msg}")
```

> **Interview gotcha:** `re.match()` only matches at the **beginning** of the string. `re.search()` matches **anywhere** in the string. For log lines where you want to match a pattern anywhere (like a status code at the end), use `re.search()`. Use `re.match()` when the pattern must start at position 0.

---

## 4. CSV

Python's `csv` module handles the edge cases of CSV parsing that naive string splitting misses. The biggest one: a field value can contain the delimiter if it's quoted. For example, `"New York, USA"` contains a comma inside quotes — `line.split(",")` would incorrectly split this into `["New York"`, `" USA\""]`. The `csv` module handles quoted fields, escaped characters, and different line endings correctly.

Two main readers:
- `csv.reader` — gives you a **list** for each row. You access fields by index: `row[0]`, `row[1]`.
- `csv.DictReader` — gives you a **dict** for each row using the header row as keys. You access fields by name: `row["hostname"]`, `row["ip"]`. This is much more readable and survives column reordering.

```python
import csv

# --- csv.reader: each row is a list ---
# newline="" is required by the csv docs to prevent issues with line endings on Windows
with open("servers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)              # creates a reader object — doesn't load file yet
    next(reader)                        # skip the header row (advance the iterator by one)
    for row in reader:                  # each row is a list of strings
        hostname = row[0]               # first column
        ip = row[1]                     # second column
        print(f"{hostname}: {ip}")

# --- csv.DictReader: each row is a dict ---
# DictReader reads the first row automatically as the header and uses those as keys
with open("servers.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)          # no need to skip header — DictReader does it for you
    for row in reader:                  # each row is a dict: {"hostname": "web01", "ip": "10.0.0.1"}
        print(row["hostname"], row["ip"])    # access by column name — survives column reordering

# --- csv.writer: write rows ---
rows = [
    ["web01", "10.0.0.1", "active"],
    ["web02", "10.0.0.2", "active"],
    ["db01",  "10.0.1.1", "standby"],
]

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["hostname", "ip", "status"])   # write header row first
    writer.writerows(rows)                           # write all data rows at once

# --- csv.DictWriter: write rows as dicts ---
data = [
    {"hostname": "web01", "ip": "10.0.0.1", "status": "active"},
    {"hostname": "db01",  "ip": "10.0.1.1", "status": "standby"},
]

with open("output.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["hostname", "ip", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()                # writes the header row from fieldnames
    writer.writerows(data)              # each dict in the list becomes a row
```

> **Common mistake:** Using `line.split(",")` to parse CSV. This works for trivial files but breaks on any field that contains a comma inside quotes, multiline fields, or files with Windows line endings. Always use the `csv` module.

---

## 5. JSON

JSON is the most common data format for APIs and config files. Python's `json` module converts between JSON strings/files and Python dicts/lists. The two main operations are **loading** (JSON → Python) and **dumping** (Python → JSON).

The naming convention trips people up: `load` vs `loads`, `dump` vs `dumps`. The rule is simple: **`s` means string**. `json.loads(s)` takes a string. `json.load(f)` takes a file object. Same for output: `json.dumps(obj)` returns a string. `json.dump(obj, f)` writes to a file.

```python
import json

# --- json.load(): read JSON from a file object ---
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)               # parses the file and returns a Python dict or list
    # config is now a regular Python dict — config["key"], config.get("key"), etc.

# --- json.loads(): read JSON from a string ---
# Common when receiving API responses or reading from subprocess output
raw = '{"host": "web01", "port": 8080}'
data = json.loads(raw)                  # parses the string → Python dict
print(data["host"])                     # "web01"

# --- json.dumps(): convert Python to a JSON string ---
obj = {"hosts": ["web01", "web02"], "count": 2}
json_string = json.dumps(obj)                       # '{"hosts": ["web01", "web02"], "count": 2}'
pretty = json.dumps(obj, indent=2)                  # pretty-printed with 2-space indentation
sorted_keys = json.dumps(obj, sort_keys=True)       # keys in alphabetical order — good for diffs
compact = json.dumps(obj, separators=(",", ":"))    # no spaces — compact for transmission

# --- json.dump(): write Python to a file as JSON ---
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=2)         # writes directly to the file — no intermediate string

# --- Handling parse errors ---
bad_json = '{"host": "web01"'           # missing closing brace
try:
    data = json.loads(bad_json)
except json.JSONDecodeError as e:
    # e.lineno and e.colno tell you WHERE in the string the parse failed
    print(f"Bad JSON at line {e.lineno}, col {e.colno}: {e.msg}")

# --- Parsing API responses (requests library) ---
import requests
r = requests.get("https://api.example.com/servers")
r.raise_for_status()                    # raises HTTPError if status code is 4xx or 5xx
data = r.json()                         # shorthand for json.loads(r.text)

# --- Types: what converts to what ---
# Python dict   → JSON object  {}
# Python list   → JSON array   []
# Python str    → JSON string  ""
# Python int    → JSON number
# Python float  → JSON number
# Python True   → JSON true
# Python None   → JSON null
# Note: Python tuples also become JSON arrays (they become lists on round-trip)
```

> **Interview gotcha:** `json.dumps()` cannot serialize Python `datetime` objects or custom classes by default — it raises `TypeError: Object of type datetime is not JSON serializable`. The fix is to convert datetimes to strings before dumping (`dt.isoformat()`), or pass a custom `default=` function to `json.dumps()`.

---

## 6. YAML

YAML is ubiquitous in DevOps — Kubernetes manifests, Ansible playbooks, Helm values, Docker Compose files, and GitHub Actions workflows are all YAML. Python's `yaml` library (PyYAML) is not in the standard library, so you need to install it: `pip install pyyaml`.

**Security warning:** There are two ways to load YAML — `yaml.safe_load()` and `yaml.load()`. **Always use `yaml.safe_load()`**. The `yaml.load()` function can execute arbitrary Python code if the YAML contains a special tag like `!!python/object`. This is a real attack vector: if you process YAML from untrusted sources (user uploads, external APIs) with `yaml.load()`, a malicious actor can run any code on your system. `yaml.safe_load()` only processes basic data types (strings, ints, lists, dicts) and refuses to execute code.

```python
# pip install pyyaml
import yaml

# --- Loading YAML from a file ---
with open("deployment.yaml", "r", encoding="utf-8") as f:
    manifest = yaml.safe_load(f)        # ALWAYS safe_load, never load()
    # Returns a Python dict/list matching the YAML structure

# --- Loading YAML from a string ---
# Useful for testing or when YAML comes from an API/subprocess
yaml_string = """
host: web01
port: 8080
tags:
  - production
  - us-east-1
"""
config = yaml.safe_load(yaml_string)    # {"host": "web01", "port": 8080, "tags": [...]}
print(config["tags"])                   # ["production", "us-east-1"]

# --- Loading a YAML file with multiple documents ---
# YAML allows multiple documents in one file separated by ---
yaml_multi = """
---
name: web01
---
name: web02
"""
# yaml.safe_load_all() returns a generator — use list() to collect all documents
docs = list(yaml.safe_load_all(yaml_multi))   # [{"name": "web01"}, {"name": "web02"}]

# --- Dumping Python to YAML ---
data = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "web", "namespace": "default"},
    "spec": {"replicas": 3},
}

# default_flow_style=False produces block style (multi-line, human-readable)
# default_flow_style=True produces flow style (compact, like JSON) — less readable
yaml_out = yaml.dump(data, default_flow_style=False)
print(yaml_out)
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   name: web
#   namespace: default
# spec:
#   replicas: 3

# Writing YAML to a file
with open("output.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, default_flow_style=False)

# --- NEVER do this ---
# yaml.load(f)              # DANGEROUS — can execute arbitrary Python code
# yaml.load(f, Loader=yaml.Loader)   # also dangerous — same as above
```

> **Security gotcha:** `yaml.load()` without a `Loader` argument was deprecated and prints a warning in newer PyYAML. Some old code uses `yaml.load(f, Loader=yaml.Loader)` to silence the warning — this is still dangerous. The only safe options are `yaml.safe_load()` or `yaml.load(f, Loader=yaml.SafeLoader)` (equivalent). If you see `yaml.load()` in a code review, flag it.

---

## 7. Temp Files

Temp files are useful when you need to write data to disk temporarily — for example, creating an input file for a subprocess, staging a config before atomically replacing the live one, or holding intermediate results that are too large for memory.

`tempfile.NamedTemporaryFile()` creates a file with a system-generated unique name and gives you a file-like object. By default, `delete=True` means the file is deleted as soon as it's closed. Set `delete=False` if you need the file to persist after the `with` block closes it (for example, to pass its path to a subprocess).

`tempfile.TemporaryDirectory()` creates a whole temporary directory and cleans it up automatically when the `with` block exits — including everything inside it.

```python
import tempfile
import os
import shutil
from pathlib import Path

# --- NamedTemporaryFile: temp file with a real path on disk ---
# delete=True (default) — file is deleted when the with block exits
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8") as f:
    f.write('{"key": "value"}')
    print(f.name)           # something like /tmp/tmp8g3kx2j1.json
    # file is accessible here
# file is DELETED here — the path no longer exists

# delete=False — file is NOT deleted when closed; you must clean up manually
with tempfile.NamedTemporaryFile(
    mode="w",
    suffix=".conf",
    delete=False,               # keep the file after the block closes
    encoding="utf-8"
) as f:
    f.write("[server]\nhost = web01\n")
    tmp_path = f.name           # save the path BEFORE the block closes

# File still exists here — pass tmp_path to a subprocess or other code
print(f"Temp file at: {tmp_path}")

# Clean up manually when you're done
os.unlink(tmp_path)             # os.unlink() deletes a single file

# --- TemporaryDirectory: temp directory, auto-cleaned ---
with tempfile.TemporaryDirectory() as tmp_dir:
    # tmp_dir is a string path like "/tmp/tmpXYZ123"
    # Write files into it as needed
    work_file = Path(tmp_dir) / "work.json"
    work_file.write_text('{"status": "processing"}', encoding="utf-8")

    another = Path(tmp_dir) / "output.txt"
    another.write_text("done", encoding="utf-8")

    # Use the files here...
# Entire directory and all its contents are deleted here

# --- mkdtemp(): create a temp directory without context manager ---
# Returns the path as a string; you are responsible for cleanup
tmp_dir = tempfile.mkdtemp(prefix="deploy-", suffix="-staging")
# prefix and suffix let you give the temp dir a recognizable name
print(tmp_dir)  # e.g., /tmp/deploy-staging-abc123

try:
    # do work in tmp_dir
    pass
finally:
    # shutil.rmtree() removes a directory and everything inside it (like rm -rf)
    shutil.rmtree(tmp_dir)      # put this in finally so cleanup happens even on error

# --- Atomic file write pattern ---
# Problem: if you write directly to a live config file and crash mid-write,
# you leave a half-written file and break the service.
# Solution: write to a temp file first, then atomically rename it over the target.
# os.replace() is atomic on the same filesystem — readers either see the old file
# or the new file, never a partial state.
import json

def write_config_atomically(path: str, data: dict):
    # Get the directory of the target file so the temp file is on the same filesystem
    dir_ = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=dir_,               # same directory = same filesystem = atomic rename works
        suffix=".tmp",
        delete=False,
        encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)
        tmp_path = f.name

    os.replace(tmp_path, path)  # atomic rename — replaces target in one OS operation
```

> **Interview gotcha:** Temp files created with `delete=False` are NOT automatically cleaned up if your script crashes. Always use a `try/finally` block (or a context manager) to ensure cleanup happens even on failure. Orphaned temp files in `/tmp` can accumulate and fill the disk — a real problem on long-running servers.
