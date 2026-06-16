# Sets & Hash Maps — Complete Guide

> The most important data structures for coding interviews.
> Almost every "easy" and many "medium" problems become trivial once you master these.

---

## Table of Contents

1. [What is Hashing?](#1-what-is-hashing)
2. [Sets](#2-sets)
3. [The `in` Operator — How it Actually Works](#3-the-in-operator--how-it-actually-works)
4. [Dictionaries (Hash Maps)](#4-dictionaries-hash-maps)
5. [The `in` Operator on Dicts](#5-the-in-operator-on-dicts)
6. [Variants: defaultdict, Counter, OrderedDict](#6-variants-defaultdict-counter-orderedddict)
7. [Comparison Table](#7-comparison-table)
8. [From Your Own Solutions](#8-from-your-own-solutions)

---

## 1. What is Hashing?

Before understanding sets and dicts, you need to understand what a **hash** is.

A **hash function** takes any value and converts it to a number (an integer index).
That number is used as the position in an internal array.

```
"hello"  →  hash()  →  9050152328547248683  →  slot 47 in memory
42       →  hash()  →  42                   →  slot 12 in memory
True     →  hash()  →  1                    →  slot 1 in memory
```

**Why does this matter?**
Because finding slot 47 in an array takes O(1) — it's just a memory address calculation.
That's why `x in my_set` is O(1) instead of O(n).

```python
# You can see Python's hash values yourself:
print(hash("hello"))   # some big integer, same every run
print(hash(42))        # 42
print(hash(True))      # 1
print(hash([1, 2, 3])) # TypeError! Lists are not hashable (explained below)
```

### What can be hashed?

| Type | Hashable? | Why |
|---|---|---|
| `int`, `float` | Yes | Immutable |
| `str` | Yes | Immutable |
| `tuple` | Yes | Immutable |
| `bool` | Yes | Immutable |
| `list` | **No** | Mutable — value can change |
| `dict` | **No** | Mutable |
| `set` | **No** | Mutable |

> **Rule of thumb:** If it can change after creation, it can't be hashed.

---

## 2. Sets

A **set** is a collection of **unique, unordered** values.
Internally it's just a hash table where only keys exist (no values attached).

### Construction

```python
# Empty set — MUST use set(), not {} (that creates an empty dict!)
s = set()

# From a literal
s = {1, 2, 3}

# From another iterable
s = set([1, 2, 2, 3, 3, 3])  # → {1, 2, 3}  (duplicates removed)
s = set("hello")              # → {'h', 'e', 'l', 'o'}  (unique chars)
s = set(range(5))             # → {0, 1, 2, 3, 4}
```

### `.add(x)` — How it Works Internally

```python
seen = set()
seen.add(42)
```

What actually happens step by step:
```
1. Python calls hash(42)          → gets integer 42
2. 42 % table_size                → determines which "bucket" (slot) to use
3. Check if that slot is empty
   - If empty: store 42 there
   - If occupied by the same value: do nothing (already exists)
   - If occupied by different value (collision): move to next slot
4. Return None
```

```python
seen = set()

seen.add(1)    # set is now {1}
seen.add(2)    # set is now {1, 2}
seen.add(1)    # set is STILL {1, 2}  — no duplicates, no error
seen.add("a")  # set is now {1, 2, 'a'}

# add() always returns None
result = seen.add(5)
print(result)  # None
```

### Other Useful Set Methods

```python
s = {1, 2, 3}

# Remove
s.remove(2)      # removes 2, raises KeyError if not found
s.discard(99)    # removes 99 if present, does NOTHING if not found (safe)
s.pop()          # removes and returns an arbitrary element

# Check size
len(s)           # number of elements

# Set math
a = {1, 2, 3}
b = {2, 3, 4}

a | b            # union:        {1, 2, 3, 4}
a & b            # intersection: {2, 3}
a - b            # difference:   {1}  (in a but not b)
a ^ b            # symmetric diff: {1, 4}  (in one but not both)

# Membership
2 in s           # True  — O(1)
99 in s          # False — O(1)
99 not in s      # True  — O(1)
```

---

## 3. The `in` Operator — How it Actually Works

This is one of the most important things to understand.

### `in` on a LIST — O(n)

```python
nums = [1, 2, 3, 4, 5]
3 in nums
```

Python has to do this:
```
Check index 0: is nums[0] == 3?  → 1 == 3? No
Check index 1: is nums[1] == 3?  → 2 == 3? No
Check index 2: is nums[2] == 3?  → 3 == 3? YES → return True
```

In the worst case (element not there), Python checks **every element**.
That's O(n) — the bigger the list, the slower the search.

### `in` on a SET — O(1)

```python
seen = {1, 2, 3, 4, 5}
3 in seen
```

Python does this:
```
1. hash(3)                   → integer 3
2. 3 % table_size            → slot number, e.g. slot 3
3. Look at slot 3 directly   → is the value there? YES → return True
```

**It jumps directly to the answer.** No looping. O(1) regardless of set size.

### Visualizing the Difference

```
LIST — searching for 7:
[3, 1, 4, 1, 5, 9, 2, 6, 7]
 ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
 ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✓   (9 comparisons)

SET — searching for 7:
hash(7) → slot 7
 slot 0 | slot 1 | ... | slot 7 | ...
                          ↑
                     jump here directly (1 operation)
```

### The Real-World Impact

```python
import time

data_list = list(range(1_000_000))
data_set  = set(range(1_000_000))

# Searching for 999_999 (near the end)
999_999 in data_list  # ~0.02 seconds  (checks ~1M elements)
999_999 in data_set   # ~0.000001 seconds (direct hash lookup)
```

---

## 4. Dictionaries (Hash Maps)

A **dict** is like a set, but each key has an associated value.
Internally: a hash table where each slot stores a (key, value) pair.

### Construction

```python
# Empty dict
d = {}
d = dict()

# From literal
d = {"name": "Alice", "age": 25}

# From list of tuples
d = dict([("a", 1), ("b", 2)])

# From two lists zipped together
keys   = ["a", "b", "c"]
values = [1,   2,   3  ]
d = dict(zip(keys, values))  # {"a": 1, "b": 2, "c": 3}
```

### Reading and Writing

```python
d = {"name": "Alice", "age": 25}

# Read
d["name"]           # "Alice"
d["missing"]        # KeyError! Key doesn't exist

# Safe read with default
d.get("name")       # "Alice"
d.get("missing")    # None  — no error
d.get("missing", 0) # 0     — custom default

# Write / update
d["age"] = 26       # update existing key
d["city"] = "NYC"   # add new key

# Delete
del d["age"]        # removes the key, raises KeyError if not found
d.pop("city")       # removes and returns the value
d.pop("x", None)    # safe pop — returns None if key missing
```

### Iterating

```python
d = {"a": 1, "b": 2, "c": 3}

# Keys only (default)
for key in d:
    print(key)          # a, b, c

# Values only
for val in d.values():
    print(val)          # 1, 2, 3

# Both — most common in interviews
for key, val in d.items():
    print(key, val)     # a 1, b 2, c 3
```

### The `.get()` Pattern — Very Important for Interviews

```python
# Counting character frequency — two ways:

# Way 1: using .get() with default 0
count = {}
for char in "hello":
    count[char] = count.get(char, 0) + 1
# {"h": 1, "e": 1, "l": 2, "o": 1}

# Way 2: checking if key exists
count = {}
for char in "hello":
    if char in count:
        count[char] += 1
    else:
        count[char] = 1

# Both produce the same result.
# Way 1 (.get) is more Pythonic and concise.
```

---

## 5. The `in` Operator on Dicts

```python
d = {"name": "Alice", "age": 25}

# IMPORTANT: 'in' checks KEYS only, not values
"name" in d    # True
"Alice" in d   # False  ← "Alice" is a value, not a key

# To check values
"Alice" in d.values()  # True  — but this is O(n)!

# To check keys explicitly (same as just 'in d')
"name" in d.keys()     # True  — O(1)
```

### How `in` Works on a Dict — Same as Set

```
d = {"a": 1, "b": 2, "c": 3}
"b" in d

1. hash("b")         → some integer
2. integer % size    → slot number
3. check that slot   → is the key "b" there? YES → return True
```

O(1) — same mechanism as a set. The key is hashed and looked up directly.

---

## 6. Variants: defaultdict, Counter, OrderedDict

### `defaultdict` — Dict with Automatic Default Values

```python
from collections import defaultdict

# Regular dict — KeyError if key missing
d = {}
d["missing"] += 1  # KeyError!

# defaultdict — creates default value automatically
d = defaultdict(int)    # default value: 0
d["missing"] += 1       # works! d["missing"] is now 1

d = defaultdict(list)   # default value: []
d["key"].append(1)      # works! d["key"] is now [1]

d = defaultdict(set)    # default value: set()
d = defaultdict(str)    # default value: ""
d = defaultdict(lambda: "N/A")  # custom default

# Common use: grouping
from collections import defaultdict

groups = defaultdict(list)
words = ["eat", "tea", "tan", "ate", "nat", "bat"]
for word in words:
    key = tuple(sorted(word))
    groups[key].append(word)

# groups = {('a','e','t'): ['eat','tea','ate'], ('a','n','t'): ['tan','nat'], ('a','b','t'): ['bat']}
```

You used this in your `anagram-groups` submission-1. It's cleaner than checking `if key not in d`.

### `Counter` — Dict Specialized for Counting

```python
from collections import Counter

# Count characters in a string
c = Counter("hello")
# Counter({'l': 2, 'h': 1, 'e': 1, 'o': 1})

# Count elements in a list
c = Counter([1, 1, 2, 3, 3, 3])
# Counter({3: 3, 1: 2, 2: 1})

# Access like a regular dict
c["l"]       # 2
c["z"]       # 0  — returns 0 for missing keys (not KeyError!)

# Most common elements
c.most_common(2)   # [(3, 3), (1, 2)]  — top 2 most frequent

# Counter math
a = Counter("aab")
b = Counter("abc")
a + b    # Counter({'a': 3, 'b': 2, 'c': 1})
a - b    # Counter({'a': 1})
a & b    # Counter({'a': 1, 'b': 1})  — minimum of each
a | b    # Counter({'a': 2, 'b': 1, 'c': 1})  — maximum of each

# Compare two counters directly
Counter("anagram") == Counter("nagaram")  # True (same chars same count)
```

You used this in your `is-anagram` submission-1. It's the most concise way to solve frequency problems.

### `OrderedDict` — Dict that Remembers Insertion Order

```python
from collections import OrderedDict

# Note: Regular dicts in Python 3.7+ ALSO maintain insertion order.
# OrderedDict is mainly useful for its .move_to_end() method.

od = OrderedDict()
od["first"] = 1
od["second"] = 2
od["third"] = 3

od.move_to_end("first")   # move "first" to the end
od.move_to_end("third", last=False)  # move "third" to the beginning

# Mainly used in LRU Cache problems
```

---

## 7. Comparison Table

| | `set` | `dict` | `defaultdict` | `Counter` |
|---|---|---|---|---|
| Stores | Keys only | Key-value pairs | Key-value pairs | Key-count pairs |
| Missing key | KeyError | KeyError | Creates default | Returns 0 |
| `in` check | O(1) | O(1) on keys | O(1) on keys | O(1) on keys |
| Best for | Membership, dedup | Mapping, lookup | Grouping | Frequency counting |
| Import needed | No | No | `from collections` | `from collections` |

### When to Use Which

```
Need to check "have I seen this before?"     → set
Need to store a value with each key?          → dict
Need to group items together?                 → defaultdict(list)
Need to count occurrences?                    → Counter  or  dict with .get(k, 0)
Need ordered operations (LRU)?                → OrderedDict
```

---

## 8. From Your Own Solutions

### `duplicate-integer` — Set for membership check
```python
seen = set()
for num in nums:
    if num in seen:   # O(1) lookup
        return True
    seen.add(num)     # O(1) insert
return False
# Total: O(n) time, O(n) space
```

### `two-integer-sum` — Dict for value→index mapping
```python
seen = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in seen:       # O(1) lookup in dict keys
        return [seen[complement], i]
    seen[num] = i                # store value → index
# Total: O(n) time, O(n) space
```

### `is-anagram` — Counter comparison
```python
Counter(s) == Counter(t)  # both are dicts of {char: count}
                          # dict equality checks all keys and values
# Total: O(n) time, O(k) space where k = unique chars
```

### `anagram-groups` — defaultdict for grouping
```python
anagram_map = defaultdict(list)
for s in strs:
    key = tuple(sorted(s))         # ('a','e','t') — hashable, order-independent
    anagram_map[key].append(s)     # no KeyError because of defaultdict
return list(anagram_map.values())
# Total: O(n * k log k) time where k = avg word length
```

---

## Quick Reference Card

```python
# SET
s = set()
s.add(x)          # add element
x in s            # O(1) membership check
s.remove(x)       # remove (KeyError if missing)
s.discard(x)      # remove (safe, no error)

# DICT
d = {}
d[key] = val      # insert/update
d.get(key, 0)     # safe read with default
key in d          # O(1) key check
for k, v in d.items()  # iterate both

# DEFAULTDICT
from collections import defaultdict
d = defaultdict(list)   # or int, set, str
d[key].append(x)        # no KeyError

# COUNTER
from collections import Counter
c = Counter(iterable)
c[key]            # count (0 if missing)
c.most_common(n)  # top n elements
```
