# Python Quick Reference — Open This When Solving a Problem

Jump to what you need:
- [Loops](#loops)
- [Strings](#strings)
- [Lists](#lists)
- [Set](#set)
- [Dict](#dict)
- [defaultdict](#defaultdict)
- [Counter](#counter)
- [Tuple](#tuple)
- [Useful Built-ins](#useful-built-ins)
- [Complexity Cheat Sheet](#complexity-cheat-sheet)
- [When to Use Which Data Structure](#when-to-use-which-data-structure)

---

## Loops

```python
# Over a list
for val in lst:

# With index + value
for i, val in enumerate(lst):

# Over a range of numbers
for i in range(n):          # 0 to n-1
for i in range(a, b):       # a to b-1
for i in range(n-1, -1, -1):  # n-1 down to 0 (reverse)

# Over dict keys and values
for key, val in d.items():

# Two pointers (while loop)
left, right = 0, len(nums) - 1
while left < right:
    left += 1
    right -= 1

# Skip current iteration
continue

# Exit loop entirely
break
```

---

## Strings

```python
s = "hello"

len(s)              # 5
s[0]                # "h"
s[-1]               # "o"
s[1:4]              # "ell"  (index 1 up to not including 4)
s[::-1]             # "olleh"  (reversed)

s.upper()           # "HELLO"
s.lower()           # "hello"
s.strip()           # removes leading/trailing spaces
s.split()           # ["hello"] — splits on whitespace
s.split(",")        # splits on comma
" ".join(["a","b"]) # "a b"  — join list into string
"".join(["a","b"])  # "ab"   — join with no separator

s.replace("l","x")  # "hexxo"
s.count("l")        # 2
"ell" in s          # True
s.startswith("he")  # True
s.endswith("lo")    # True

# Iterate over characters
for char in s:
    ...

# String is immutable — you CANNOT do s[0] = "H"
# To modify: convert to list, change, join back
lst = list(s)
lst[0] = "H"
s = "".join(lst)    # "Hello"

# Sorted characters — useful for anagram problems
sorted("eat")              # ['a', 'e', 't']
"".join(sorted("eat"))     # "aet"
```

---

## Lists

```python
lst = [1, 2, 3]

# Access
lst[0]          # first element
lst[-1]         # last element
lst[1:3]        # [2, 3]  — slice

# Add
lst.append(4)       # [1, 2, 3, 4]  — O(1)
lst.extend([5, 6])  # adds multiple items
lst.insert(0, 99)   # insert at index — O(n), avoid if possible

# Remove
lst.pop()           # remove + return last — O(1)
lst.pop(i)          # remove + return at index i — O(n)
lst.remove(val)     # remove first occurrence of val

# Info
len(lst)
val in lst          # O(n) — slow for large lists, use set instead
lst.count(val)      # how many times val appears
lst.index(val)      # index of first occurrence

# Sort
lst.sort()              # sorts IN PLACE, modifies lst, O(n log n)
sorted(lst)             # returns NEW sorted list, original unchanged
lst.sort(reverse=True)  # descending

# Copy
lst.copy()          # shallow copy
lst[:]              # also a shallow copy

# List of Lists (2D)
grid[row][col]
for row in grid:
    for val in row:
        ...

# Safe 2D grid creation (n rows, m cols, filled with 0)
grid = [[0] * m for _ in range(n)]
```

---

## Set

```python
s = set()           # empty set — NOT {}, that's an empty dict!
s = {1, 2, 3}       # set literal
s = set([1,2,2,3])  # from list — removes duplicates → {1, 2, 3}

s.add(x)            # add element — O(1)
s.remove(x)         # remove — KeyError if missing
s.discard(x)        # remove — no error if missing
x in s              # O(1) membership check ← KEY ADVANTAGE OVER LIST
len(s)

# Set operations
a | b   # union
a & b   # intersection
a - b   # difference (in a, not in b)
```

**Use a set when:** you need fast "have I seen this?" checks, or need unique values.

---

## Dict

```python
d = {}
d = {"a": 1, "b": 2}

# Read
d["a"]              # 1 — KeyError if missing
d.get("a")          # 1 — None if missing (safe)
d.get("x", 0)       # 0 — custom default if missing

# Write
d["key"] = val      # add or update
del d["key"]        # delete — KeyError if missing
d.pop("key", None)  # delete + return, safe if missing

# Check
"key" in d          # O(1) — checks KEYS only, not values
len(d)

# Iterate
for key in d:               # keys
for val in d.values():      # values
for key, val in d.items():  # both

# Frequency count pattern
count = {}
for x in items:
    count[x] = count.get(x, 0) + 1
```

**Use a dict when:** you need to map a key to a value (index, count, group).

---

## defaultdict

```python
from collections import defaultdict

d = defaultdict(list)   # missing key → []
d = defaultdict(int)    # missing key → 0
d = defaultdict(set)    # missing key → set()

# Grouping pattern
d = defaultdict(list)
for item in items:
    key = some_function(item)
    d[key].append(item)        # no KeyError even on first append

return list(d.values())        # List[List[...]]
```

**Use defaultdict when:** you're grouping items and don't want to check `if key in d` every time.

---

## Counter

```python
from collections import Counter

c = Counter("hello")            # {'l':2, 'h':1, 'e':1, 'o':1}
c = Counter([1, 1, 2, 3])       # {1:2, 2:1, 3:1}

c["l"]              # 2
c["z"]              # 0  — no KeyError for missing keys
c.most_common(2)    # [(most_freq, count), (second, count)]

# Compare two frequency maps
Counter(s) == Counter(t)    # True if same chars same count (anagram check)

# Counter math
c1 + c2     # add counts
c1 - c2     # subtract (drops zeros and negatives)
c1 & c2     # minimum of each
c1 | c2     # maximum of each
```

**Use Counter when:** you need to count frequencies and compare them.

---

## Tuple

```python
t = (1, 2, 3)
t = tuple([1, 2, 3])    # from list
t = tuple("abc")        # ('a', 'b', 'c')

t[0]            # 1
len(t)          # 3
1 in t          # True

# Tuples are IMMUTABLE — you cannot change them after creation
# This makes them HASHABLE → can be used as dict keys or in sets

# Common use: sorted characters as a dict key
key = tuple(sorted("eat"))   # ('a', 'e', 't')
d[key] = ...                 # valid — tuple is hashable

# Why not just use a sorted string as key?
# Both work. tuple and str are both hashable.
"".join(sorted("eat"))   # "aet"  ← also valid as a key
tuple(sorted("eat"))     # ('a','e','t')  ← also valid as a key
```

---

## Useful Built-ins

```python
len(x)              # length of string, list, dict, set
min(iterable)       # smallest value
max(iterable)       # largest value
sum(iterable)       # sum of all values
abs(x)              # absolute value, abs(-5) = 5

sorted(iterable)                # new sorted list
sorted(iterable, reverse=True)  # descending
sorted(words, key=len)          # sort by string length
sorted(words, key=lambda w: w[0])  # sort by first character

range(n)            # 0 to n-1
range(a, b)         # a to b-1
range(a, b, step)   # a to b-1 by step
list(range(5))      # [0, 1, 2, 3, 4]

enumerate(lst)               # (0,val), (1,val), ...
zip([1,2,3], ["a","b","c"])  # (1,"a"), (2,"b"), (3,"c")

any([False, True, False])    # True  — is at least one truthy?
all([True, True, True])      # True  — are all truthy?

int("42")       # "42" → 42
str(42)         # 42 → "42"
float("3.14")   # "3.14" → 3.14
list("abc")     # ['a', 'b', 'c']

# Math
x ** 2          # x squared
x ** 0.5        # square root
x // 2          # integer division (floor), 7//2 = 3
x % 2           # modulo (remainder), 7%2 = 1

# Infinity — useful for min/max problems
float("inf")    # positive infinity
float("-inf")   # negative infinity
```

---

## Complexity Cheat Sheet

| Operation | Data Structure | Complexity |
|---|---|---|
| `x in list` | list | O(n) ← SLOW |
| `x in set` | set | O(1) ← FAST |
| `x in dict` | dict (key check) | O(1) ← FAST |
| `dict[key]` | dict | O(1) |
| `set.add(x)` | set | O(1) |
| `list.append(x)` | list | O(1) |
| `list.insert(0,x)` | list | O(n) ← SLOW |
| `list.pop()` | list (from end) | O(1) |
| `list.pop(0)` | list (from front) | O(n) ← SLOW |
| `sorted(lst)` | — | O(n log n) |
| `"".join(sorted(s))` | — | O(k log k) |
| Single loop | — | O(n) |
| Nested loops | — | O(n²) |

---

## When to Use Which Data Structure

| Situation | Use |
|---|---|
| "Have I seen this value before?" | `set` |
| "Remove duplicates from a list" | `set(lst)` |
| "Count how many times each value appears" | `Counter` or `dict` with `.get(k,0)+1` |
| "Map a value to an index" | `dict` |
| "Group items that share a property" | `defaultdict(list)` |
| "Need fast lookup AND store a value" | `dict` |
| "Need a key that's a list (unhashable)" | Convert to `tuple` first |
| "Find two numbers that sum to target" | `dict` — store value→index |
| "Check if two strings are anagrams" | `Counter(s) == Counter(t)` |
| "Group anagrams together" | `defaultdict(list)`, key = sorted string |
