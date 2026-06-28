# Python Basics — SRE / DevOps Tutor Reference

This file is written as a tutor, not a cheatsheet. Every section explains **what the thing is and why you need it** before showing code, and every non-obvious line has a comment. Read the explanations — don't skip straight to the code.

---

## 1. Variables & Types

Python is **dynamically typed**, meaning you don't declare a variable's type upfront — Python figures it out at runtime from the value you assign. This is convenient but it also means bugs from passing the wrong type don't show up until the code actually runs. Understanding what types exist, and what makes each one unique, is the foundation of writing correct Python.

The built-in types you'll use constantly in SRE scripts: `int` (whole numbers), `str` (text), `list` (ordered, mutable sequence), `dict` (key-value pairs), `set` (unordered collection with no duplicates), and `tuple` (immutable sequence — frozen list).

**Why does immutability matter?** A `tuple` can be used as a dictionary key; a `list` cannot. Python requires dict keys to be *hashable*, and mutable objects like lists aren't hashable because their contents can change. This comes up when you want to count pairs or coordinates.

```python
# Assigning variables — no type declaration needed
x = 42                        # int
s = "hello"                   # str
lst = [1, 2, 3]               # list — ordered, can be changed after creation
d = {"key": "value"}          # dict — key/value store, keys must be unique
st = {1, 2, 2, 3}            # set — {1, 2, 3}; duplicates are silently dropped
t = (1, 2, 3)                 # tuple — like a list but immutable (can't change it)

# --- Why isinstance() is preferred over type(x) == int ---
# type(x) == int returns False if x is a subclass of int.
# isinstance() returns True for the type AND any subclass — it's more flexible
# and is what Python's own standard library uses internally.
print(type(x))                # <class 'int'> — tells you the exact type
print(isinstance(x, int))     # True — preferred in real code
print(isinstance(x, (int, float)))  # True — isinstance accepts a tuple of types,
                                    # so you can check multiple types in one call

# --- Unique properties of each type ---
# set: fast membership test (O(1) average), automatically deduplicates
hosts = {"web01", "web02", "web01"}   # automatically becomes {"web01", "web02"}
print("web01" in hosts)               # True — fast lookup, good for allow/deny lists

# tuple: immutable — you cannot append, remove, or change elements
point = (10, 20)
# point[0] = 99  # This would raise TypeError — tuples don't support item assignment
coord_count = {point: 5}             # tuples CAN be dict keys because they're hashable
# coord_count[[10, 20]: 5]           # This would fail — lists are NOT hashable

# dict: keys must be unique; later assignment overwrites
config = {"timeout": 30, "timeout": 60}   # "timeout" appears twice
print(config)                              # {"timeout": 60} — last value wins
```

> **Common mistake:** Using `type(x) == list` instead of `isinstance(x, list)`. The `==` check will return `False` for subclasses, which breaks code silently when someone passes a custom list-like object. Always use `isinstance()`.

---

## 2. Control Flow

Python uses **indentation** (spaces or tabs — pick one and never mix) to define blocks. There are no curly braces like in C or JavaScript. If your indentation is wrong, the code either crashes with `IndentationError` or silently does the wrong thing. The standard is 4 spaces per level.

List comprehensions are Python's compact way to build a list using a `for` loop in a single expression. They're faster than an explicit loop and are considered idiomatic Python — you'll see them everywhere. The mental model: `[expression for item in iterable if condition]`.

```python
x = 10

# --- if / elif / else ---
# elif is short for "else if" — Python has no switch statement (before 3.10)
if x > 10:
    print("big")
elif x == 10:                 # checked only if the first condition was False
    print("exactly ten")
else:                         # runs if none of the above matched
    print("small")

# --- for loop with range() ---
# range(5) produces 0, 1, 2, 3, 4 — it does NOT include the stop value
for i in range(5):
    if i == 2:
        continue              # skip the rest of this iteration, go to next i
    if i == 4:
        break                 # stop the loop entirely — don't run any more iterations
    print(i)                  # prints 0, 1, 3

# range(start, stop, step) — start at 1, stop before 10, step by 2
for i in range(1, 10, 2):    # 1, 3, 5, 7, 9
    print(i)

# --- while loop ---
count = 0
while count < 3:              # keep looping as long as this is True
    count += 1                # count = count + 1
# count is now 3

# --- List comprehension: the short form ---
# Long form:
squares_long = []
for x in range(6):
    if x % 2 == 0:            # % is modulo — x % 2 == 0 means x is even
        squares_long.append(x ** 2)   # x**2 is x to the power of 2

# Short form — same result, one line:
squares = [x**2 for x in range(6) if x % 2 == 0]
# Read it as: "give me x squared, for each x in range(6), but only if x is even"
# Result: [0, 4, 16]

# List comprehension to filter log lines containing "ERROR"
log_lines = ["INFO started", "ERROR disk full", "INFO ok", "ERROR timeout"]
errors = [line for line in log_lines if "ERROR" in line]
# Result: ["ERROR disk full", "ERROR timeout"]

# Dict comprehension — same idea but builds a dict
word_lengths = {word: len(word) for word in ["cat", "elephant", "dog"]}
# Result: {"cat": 3, "elephant": 8, "dog": 3}
```

> **Interview gotcha:** `range()` does NOT include the stop value. `range(5)` gives you 0–4. This surprises people coming from inclusive-range languages. Also: list comprehensions create a new list in memory — if you only need to iterate once, use a generator expression `(x for x in ...)` instead, which is lazy and uses less memory.

---

## 3. Functions

`def` creates a **reusable block of code** that you can call by name. Functions reduce repetition and make code testable. Python functions have several parameter types: regular positional args, args with default values, `*args` for a variable number of positional args, and `**kwargs` for a variable number of keyword args.

**The mutable default argument trap** is one of the most common Python bugs. When Python sees `def fn(lst=[])`, it creates that empty list **once** when the function is defined — not each time the function is called. Every call that doesn't pass a list shares the **same** list object in memory. So if one call appends to it, the next call sees the modified list. The fix is to use `None` as the default and create the fresh list inside the function body.

```python
# --- Basic function with a default argument ---
def greet(name: str, greeting: str = "Hello") -> str:
    # greeting has a default — callers can omit it
    return f"{greeting}, {name}!"

print(greet("Alice"))              # "Hello, Alice!"    — uses the default
print(greet("Alice", "Hi"))       # "Hi, Alice!"       — caller overrides the default
print(greet(greeting="Hey", name="Bob"))  # keyword args can come in any order

# --- *args: accept any number of positional arguments ---
# *args collects all extra positional arguments into a TUPLE named args
def log_event(*args):
    # args is a tuple: ("deploy", "web01", "success") for example
    for item in args:
        print(item)

log_event("deploy", "web01", "success")  # works with any number of positional args

# --- **kwargs: accept any number of keyword arguments ---
# **kwargs collects all extra keyword arguments into a DICT named kwargs
def configure(**kwargs):
    # kwargs is a dict: {"timeout": 30, "retries": 3} for example
    for key, value in kwargs.items():
        print(f"{key} = {value}")

configure(timeout=30, retries=3, region="us-east-1")

# --- The mutable default argument trap ---
# BAD — this list is created ONCE when Python loads the function definition.
# Every call that omits lst shares the SAME list object.
def append_bad(item, lst=[]):
    lst.append(item)
    return lst

print(append_bad(1))   # [1]   — looks fine
print(append_bad(2))   # [1, 2] — SURPRISE: the previous call's value is still there!
print(append_bad(3))   # [1, 2, 3] — keeps growing across calls

# GOOD — use None as the default sentinel; create a fresh list inside the function
def append_good(item, lst=None):
    if lst is None:           # None is the standard sentinel for "no value passed"
        lst = []              # this creates a NEW list on every call that needs it
    lst.append(item)
    return lst

print(append_good(1))  # [1]
print(append_good(2))  # [2] — fresh list each time, no contamination

# --- Lambda: anonymous single-expression function ---
# Use lambdas for short throw-away functions, like sort keys
square = lambda x: x ** 2        # equivalent to def square(x): return x**2

servers = [{"name": "web02", "ip": "10.0.0.2"}, {"name": "web01", "ip": "10.0.0.1"}]
sorted_servers = sorted(servers, key=lambda s: s["name"])  # sort by the "name" field
```

> **Interview gotcha:** The mutable default argument trap. Interviewers love this. The fix is always `def fn(lst=None)` + `if lst is None: lst = []`. This comes up with lists, dicts, and sets as defaults — any mutable object.

---

## 4. Error Handling

Python uses `try/except` to handle code that might fail — network calls, file reads, type conversions, etc. The full structure has four clauses, each with a specific role:

- **`try`** — the code you want to run (the risky part)
- **`except`** — runs only if the specified exception is raised inside `try`
- **`else`** — runs only if NO exception was raised — useful for code that should only happen on success
- **`finally`** — ALWAYS runs, regardless of success or failure — use this for cleanup (closing connections, releasing locks)

Sometimes you want to log an error and then re-raise it so the caller still sees the crash. A bare `raise` (no argument) re-raises the exact same exception with the original stack trace intact — you don't lose information about where the error started.

```python
# --- Full try/except/else/finally structure ---
try:
    # This is the risky code — if it raises an exception, Python jumps to except
    result = int("abc")           # this will raise ValueError: invalid literal...

except ValueError as e:
    # This block runs ONLY if a ValueError was raised
    # 'e' is the exception object — you can print it or inspect it
    print(f"Conversion failed: {e}")

except (KeyError, IndexError) as e:
    # You can catch multiple exception types in one except clause
    # This runs if either KeyError OR IndexError was raised
    print(f"Lookup error: {e}")

except Exception as e:
    # Exception is the base class for almost all exceptions — this is a catch-all
    # Be careful: this hides bugs if used too broadly
    print(f"Unexpected error: {e}")

else:
    # This block runs ONLY if no exception was raised in the try block
    # Good place for code that depends on the try succeeding
    print(f"Conversion succeeded: {result}")

finally:
    # This block ALWAYS runs — exception or not
    # Use it to release resources: close files, disconnect from DB, release locks
    print("Done — cleaning up")

# --- Raising your own exceptions ---
def set_timeout(seconds: int):
    if seconds < 0:
        # You can raise any exception with a descriptive message
        raise ValueError(f"Timeout must be positive, got {seconds}")
    # ... rest of function

# --- Re-raising after logging — preserving the stack trace ---
import logging

def risky_operation():
    raise ConnectionError("DB unreachable")

try:
    risky_operation()
except Exception as e:
    # Log the error with exc_info=True to include the full stack trace in the log
    logging.error("Operation failed: %s", e, exc_info=True)
    raise    # bare raise — re-raises the SAME exception; caller sees the original traceback

# --- Common exceptions you'll encounter in SRE scripts ---
# ValueError       — wrong value (int("abc"), negative timeout)
# KeyError         — missing dict key (d["missing"])
# FileNotFoundError — file doesn't exist (open("nope.txt"))
# TypeError        — wrong type passed (len(42) — int has no length)
# AttributeError   — object has no such attribute ("hello".push("x"))
# PermissionError  — OS denied access (reading /etc/shadow without root)
# ConnectionError  — network / socket issue
```

> **Common mistake:** Using a bare `except:` with no exception type — this catches everything including `KeyboardInterrupt` (Ctrl+C) and `SystemExit`, making your script impossible to kill cleanly. Always name the exception: `except Exception as e:` at the broadest.

---

## 5. String Operations

Strings are immutable in Python — every method that "modifies" a string actually returns a new string. This matters for performance: don't concatenate strings in a loop with `+` (creates a new string on every iteration); use `"".join(list)` instead.

**f-strings** (formatted string literals) are the modern way to embed variables in strings. Prefix the string with `f` and put any Python expression inside `{}`. They were added in Python 3.6 and are now the standard — prefer them over `.format()` or `%` formatting.

```python
# --- f-strings: embedding variables and expressions ---
host = "web01"
cpu = 87.5

msg = f"Host: {host}, CPU: {cpu}%"          # "Host: web01, CPU: 87.5%"
msg = f"Host: {host!r}"                     # !r applies repr() — adds quotes: "Host: 'web01'"
msg = f"CPU: {cpu:.1f}%"                    # :.1f = one decimal place → "CPU: 87.5%"
msg = f"CPU: {cpu:.0f}%"                    # :.0f = no decimals → "CPU: 88%"
msg = f"Hex: {255:#x}"                      # #x = hex format → "Hex: 0xff"

# --- .strip() — remove leading and trailing whitespace (or specific chars) ---
raw = "   ERROR: disk full\n"
clean = raw.strip()                         # "ERROR: disk full" — removes spaces AND \n

raw2 = "###important###"
clean2 = raw2.strip("#")                   # "important" — removes the # chars on both ends

# --- .split() — split a string into a list ---
line = "web01 10.0.0.1 active"
parts = line.split()                        # ["web01", "10.0.0.1", "active"] — splits on whitespace
parts = line.split(" ", maxsplit=1)         # ["web01", "10.0.0.1 active"] — stop after 1 split

csv_line = "alice,30,engineer"
fields = csv_line.split(",")               # ["alice", "30", "engineer"]

# --- .join() — join a list into a string ---
# join is the REVERSE of split; the string you call it on is the separator
words = ["restarted", "web01", "successfully"]
sentence = " ".join(words)                  # "restarted web01 successfully"
csv_out = ",".join(["alice", "30", "eng"]) # "alice,30,eng"
path = "/".join(["", "var", "log", "app"]) # "/var/log/app"

# --- Other useful string methods ---
"  hello  ".strip()                        # "hello"
"hello world".upper()                      # "HELLO WORLD"
"HELLO".lower()                            # "hello"
"hello world".replace("world", "Python")  # "hello Python"
"error: disk".startswith("error")         # True
"app.log".endswith(".log")                # True
"  ".strip() == ""                        # True — useful for checking blank lines

# --- Regex (re module) ---
# re is Python's built-in regular expression library.
# Use it when string methods aren't powerful enough (patterns, optional parts, groups).
import re

line = "2024-01-15 12:03:45 GET /api/health 200"

# re.search() looks for the pattern ANYWHERE in the string.
# It returns a Match object if found, or None if not — always check before calling .group()
m = re.search(r'(\d{3})$', line)          # look for 3 digits at the END of the string
                                           # r'...' is a raw string — backslashes aren't escape chars
if m:
    status_code = m.group(1)              # .group(1) returns the first captured group → "200"
    # .group(0) or .group() returns the whole match

# re.findall() returns ALL matches as a list of strings — no Match object, just strings
all_numbers = re.findall(r'\d+', line)    # ['\d+' matches one or more digits]
# Result: ['2024', '01', '15', '12', '03', '45', '200']

# re.sub() substitutes (replaces) matches with a replacement string
cleaned = re.sub(r'\s+', ' ', line)       # collapse multiple whitespace chars into one space

# re.compile() pre-compiles a pattern — more efficient if you're using the same pattern many times
pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')   # matches a date like 2024-01-15
m = pattern.search(line)
```

> **Interview gotcha:** `.split()` with no argument splits on ANY whitespace and also removes empty strings from the result. `"a  b".split()` → `["a", "b"]`. But `"a  b".split(" ")` → `["a", "", "b"]` — the empty string stays in. This difference trips people up when parsing log lines that use multiple spaces as separators.

---

## 6. Data Structures

`dict` is the most important data structure in SRE Python. Almost every real-world SRE task — counting events, grouping servers, building configs — uses dicts. Know the safe access patterns cold.

`defaultdict` from the `collections` module is a dict that automatically creates a default value when you access a missing key. This saves you from writing `if key not in d: d[key] = 0` before every increment.

```python
from collections import defaultdict, Counter

# --- dict: the workhorse ---
config = {"host": "db01", "port": 5432, "timeout": 30}

# Safe key access — d['key'] raises KeyError if missing; .get() returns None
host = config.get("host")                 # "db01"
missing = config.get("region")            # None — no crash
missing = config.get("region", "us-east-1")  # "us-east-1" — custom default

# Iterating a dict
for key in config:                        # iterates over keys
    print(key)

for key, value in config.items():         # iterates over (key, value) pairs — most common
    print(f"{key}: {value}")

# Merging dicts
extra = {"ssl": True, "port": 3306}
merged = {**config, **extra}             # ** unpacks a dict; later keys overwrite earlier ones
                                          # merged["port"] is 3306 — extra overwrites config
config.update(extra)                      # same merge but IN PLACE — modifies config directly

# dict comprehension
servers = ["web01", "web02", "db01"]
status = {s: "unknown" for s in servers}  # {"web01": "unknown", "web02": "unknown", ...}

# --- list: ordered, mutable ---
hosts = ["web01", "web02", "db01"]
hosts.append("cache01")                   # add ONE item to the end
hosts.extend(["lb01", "lb02"])           # add MULTIPLE items (extend takes an iterable)
hosts.insert(0, "mgmt01")               # insert at index 0 (front)
hosts.remove("db01")                     # remove first occurrence of this value
popped = hosts.pop()                     # remove and return the LAST item
popped = hosts.pop(0)                    # remove and return item at index 0

sorted_hosts = sorted(hosts)             # returns a NEW sorted list — original unchanged
hosts.sort()                             # sorts IN PLACE — modifies hosts, returns None
hosts.sort(reverse=True)                 # reverse order

# --- enumerate: loop with index AND value ---
for i, host in enumerate(hosts):         # enumerate returns (index, value) pairs
    print(f"{i}: {host}")               # 0: web01, 1: web02, ...

# --- zip: loop over two lists in parallel ---
ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
names = ["web01", "web02", "web03"]
for name, ip in zip(names, ips):         # zip pairs them up: ("web01", "10.0.0.1"), ...
    print(f"{name} → {ip}")

# --- defaultdict: auto-initializes missing keys ---
# defaultdict(int) means: if you access a missing key, create it with value 0 (int())
error_count = defaultdict(int)

logs = ["ERROR disk", "INFO ok", "ERROR timeout", "ERROR disk"]
for log in logs:
    if log.startswith("ERROR"):
        error_type = log.split()[1]      # "disk", "timeout", "disk"
        error_count[error_type] += 1    # no KeyError even on first access — starts at 0

# Result: {"disk": 2, "timeout": 1}

# defaultdict(list) means: missing key gets an empty list [] as default
servers_by_role = defaultdict(list)
data = [("web", "web01"), ("db", "db01"), ("web", "web02")]
for role, name in data:
    servers_by_role[role].append(name)   # no need to check if key exists first
# Result: {"web": ["web01", "web02"], "db": ["db01"]}

# --- Counter: count occurrences in a sequence ---
events = ["login", "logout", "login", "login", "error", "logout"]
freq = Counter(events)                    # Counter({"login": 3, "logout": 2, "error": 1})
print(freq["login"])                     # 3
print(freq.most_common(2))              # [("login", 3), ("logout", 2)] — top 2
```

> **Common mistake:** Modifying a dict or list while iterating over it. This raises `RuntimeError: dictionary changed size during iteration`. Fix: iterate over `list(d.keys())` to iterate over a snapshot, or build a separate list of items to remove and delete them after the loop.

---

## 7. Type Hints

Type hints tell **readers and tools** what types a function expects and returns — they don't change how Python actually runs your code at all. A function with type hints is self-documenting: you can understand what it does without reading the whole body. IDEs and linters (like mypy) also use them to catch bugs before runtime.

`Optional[str]` means the value can be a `str` OR `None`. This is very common for function return values that might not find anything. `Union[str, int]` means the value can be one of several types. In Python 3.10+, you can write these as `str | None` and `str | int`.

```python
from typing import Optional, Union, List, Dict, Tuple, Callable, Any

# --- Basic type hints on a function ---
# Without hints: def parse(s): — reader has to guess what s is and what comes back
# With hints: it's instantly clear
def parse_port(s: str) -> Optional[int]:
    # Takes a string, returns an int if successful, or None if it fails
    try:
        port = int(s)
        if 1 <= port <= 65535:           # valid port range
            return port
        return None                      # out of range — return None, not an exception
    except ValueError:
        return None                      # couldn't convert — return None

result = parse_port("8080")             # returns 8080 (int)
result = parse_port("abc")             # returns None

# --- Optional is just shorthand for Union[X, None] ---
# Optional[int] is identical to Union[int, None]
def find_host(ip: str) -> Optional[str]:   # might not find a host for the IP
    ...

# --- Union: accepts multiple types ---
def stringify(val: Union[str, int, float]) -> str:
    return str(val)

# Python 3.10+ shorthand — cleaner syntax, same meaning
def parse_v2(s: str) -> int | None:      # same as Optional[int]
    ...

def stringify_v2(val: str | int | float) -> str:
    return str(val)

# --- Type hints for collections ---
# Use lowercase list/dict/tuple in Python 3.9+
def run_command(cmd: list[str]) -> tuple[int, str]:
    # cmd is a list of strings (like ["kubectl", "get", "pods"])
    # returns a tuple of (exit_code, output)
    ...

def build_env(base: dict[str, str], overrides: dict[str, str]) -> dict[str, str]:
    return {**base, **overrides}

# --- Callable: a function type hint ---
# Use Callable[[arg_types], return_type] to type-hint a function argument
def retry(fn: Callable[[], Any], attempts: int = 3) -> Any:
    # fn is a function that takes no arguments and returns anything
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise

# --- Why bother if Python doesn't enforce them? ---
# 1. Readers understand your function instantly without reading the body
# 2. IDEs give you autocomplete based on the return type
# 3. mypy or pyright can catch type mismatches before you run the code
# 4. In team environments, type hints are documentation that can't go stale the way
#    comments do — the linter enforces them
```

> **Interview gotcha:** Type hints are purely informational at runtime. Python will NOT raise an error if you pass an `int` to a function that says it expects a `str`. They're a development-time tool. If you need runtime type enforcement, use `isinstance()` checks inside the function body.
