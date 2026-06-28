# Python Basics — SRE Reference

## 1. Variables & Types

```python
# Built-in types
x: int = 42
s: str = "hello"
lst: list = [1, 2, 3]
d: dict = {"key": "value"}
st: set = {1, 2, 3}           # unordered, unique
t: tuple = (1, 2, 3)          # immutable

# Type inspection
type(x)           # <class 'int'>
isinstance(x, int)            # True — preferred over type() ==
isinstance(x, (int, float))   # True — checks multiple types
```

---

## 2. Control Flow

```python
# if/elif/else
if x > 0:
    pass
elif x == 0:
    pass
else:
    pass

# for/while
for i in range(10):
    if i == 3: continue       # skip
    if i == 7: break          # stop

while True:
    break

# List comprehension
squares = [x**2 for x in range(10) if x % 2 == 0]
flat = [item for sublist in nested for item in sublist]

# Dict comprehension
inv = {v: k for k, v in d.items()}
```

---

## 3. Functions

```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"

# *args / **kwargs
def log(*args, **kwargs):
    print(args)    # tuple of positional args
    print(kwargs)  # dict of keyword args

# Lambda — one-liner, no statements
square = lambda x: x**2
sorted_list = sorted(items, key=lambda x: x["name"])

# GOTCHA: mutable default arg — shared across all calls
def bad(lst=[]):          # BAD — list is created once
    lst.append(1)
    return lst            # grows on every call!

def good(lst=None):       # GOOD — create fresh each call
    if lst is None:
        lst = []
    lst.append(1)
    return lst
```

---

## 4. Error Handling

```python
# Full try/except structure
try:
    result = int("abc")
except ValueError as e:
    print(f"Bad value: {e}")
except (KeyError, IndexError) as e:
    print(f"Lookup failed: {e}")
else:
    print("No exception — runs only on success")
finally:
    print("Always runs — cleanup here")

# Raise
if value < 0:
    raise ValueError(f"Expected positive, got {value}")

# Re-raise after logging — preserve original traceback
import logging
try:
    risky_operation()
except Exception as e:
    logging.error("Operation failed: %s", e, exc_info=True)
    raise                 # re-raise same exception, stack intact

# Common exceptions to know
# ValueError       — wrong value (int("abc"))
# KeyError         — missing dict key
# FileNotFoundError — file doesn't exist
# TypeError        — wrong type passed
# AttributeError   — missing attribute
# PermissionError  — file/OS permission denied
```

---

## 5. String Operations

```python
name = "  hello world  "

# f-strings (3.6+)
msg = f"User: {name.strip()!r}"     # !r for repr()
pi = f"{3.14159:.2f}"               # formatting

# Common methods
name.strip()                        # remove leading/trailing whitespace
name.split()                        # split on whitespace → list
",".join(["a", "b", "c"])          # "a,b,c"
"error".startswith("err")           # True
"access.log".endswith(".log")       # True
"hello".upper() / "HELLO".lower()

# Regex
import re

line = "2024-01-15 12:03:45 GET /api/health 200"

m = re.search(r'(\d{3})$', line)   # search anywhere in string
if m:
    code = m.group(1)               # "200"

matches = re.findall(r'\d+', line) # ['2024', '01', '15', ...]

cleaned = re.sub(r'\s+', ' ', line) # collapse whitespace
```

---

## 6. Data Structures

```python
# dict
d = {"a": 1, "b": 2}
d.get("c", 0)                    # 0 — safe missing key access
d.items()                        # [("a", 1), ("b", 2)]
d.update({"c": 3})               # merge in-place
d2 = {**d, "d": 4}              # merge → new dict (3.5+)

# list
lst = [3, 1, 2]
lst.append(4)                    # [3, 1, 2, 4]
lst.extend([5, 6])               # [3, 1, 2, 4, 5, 6]
sorted(lst)                      # new sorted list
lst.sort(reverse=True)           # in-place

# enumerate / zip
for i, val in enumerate(["a", "b", "c"]):
    print(i, val)                # 0 a, 1 b, 2 c

for k, v in zip(keys, values):
    print(k, v)                  # pairs

# defaultdict / Counter
from collections import defaultdict, Counter
counts = defaultdict(int)        # missing key → 0
freq = Counter(["a", "b", "a"]) # {"a": 2, "b": 1}
freq.most_common(3)              # top 3
```

---

## 7. Type Hints

```python
from typing import Optional, Union, Any

def parse(s: str) -> Optional[int]:    # returns int or None
    try:
        return int(s)
    except ValueError:
        return None

def process(val: Union[str, int]) -> str:
    return str(val)

# 3.10+ shorthand
def parse_v2(s: str) -> int | None:
    ...

# Collections
def run(cmd: list[str], env: dict[str, str]) -> tuple[int, str]:
    ...

# Callable
from typing import Callable
def retry(fn: Callable[[], Any], attempts: int = 3) -> Any:
    ...
```
