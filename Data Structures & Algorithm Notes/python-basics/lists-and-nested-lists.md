# Lists & Lists of Lists — Complete Guide

> A list is the most common data structure in Python interviews.
> Understanding nested lists (list of lists) unlocks matrix problems, grouping problems, and graph problems.

---

## Table of Contents

1. [Lists — The Basics](#1-lists--the-basics)
2. [Indexing and Slicing](#2-indexing-and-slicing)
3. [Modifying a List](#3-modifying-a-list)
4. [Iterating a List](#4-iterating-a-list)
5. [List of Lists — What It Is](#5-list-of-lists--what-it-is)
6. [Creating a List of Lists](#6-creating-a-list-of-lists)
7. [Reading and Writing in a List of Lists](#7-reading-and-writing-in-a-list-of-lists)
8. [Iterating a List of Lists](#8-iterating-a-list-of-lists)
9. [Common Patterns in Interview Problems](#9-common-patterns-in-interview-problems)
10. [From Your Own Solutions](#10-from-your-own-solutions)

---

## 1. Lists — The Basics

A list is an **ordered, mutable** sequence of values.
Ordered = position matters. Mutable = you can change it after creation.

```python
# Creating lists
nums   = [1, 2, 3, 4, 5]
words  = ["apple", "banana", "cherry"]
mixed  = [1, "hello", True, 3.14]     # can hold any types
empty  = []                            # empty list
nested = [[1, 2], [3, 4], [5, 6]]     # list of lists

# Length
len(nums)    # 5
```

---

## 2. Indexing and Slicing

### Indexing — Accessing One Element

```
Index:   0     1     2     3     4
List:  ["a", "b", "c", "d", "e"]
Index:  -5    -4    -3    -2    -1   ← negative indices count from the end
```

```python
lst = ["a", "b", "c", "d", "e"]

lst[0]    # "a"  — first element
lst[4]    # "e"  — last element (by positive index)
lst[-1]   # "e"  — last element (easiest way)
lst[-2]   # "d"  — second to last
lst[10]   # IndexError! — index out of range
```

### Slicing — Accessing a Range of Elements

Syntax: `lst[start : stop : step]`
- `start` is **inclusive**
- `stop` is **exclusive** (goes up to but NOT including stop)

```python
lst = [0, 1, 2, 3, 4, 5, 6, 7]

lst[2:5]     # [2, 3, 4]       — index 2 up to (not including) 5
lst[:3]      # [0, 1, 2]       — from beginning up to index 3
lst[4:]      # [4, 5, 6, 7]    — from index 4 to end
lst[:]       # [0, 1, 2, 3, 4, 5, 6, 7]  — full copy
lst[::2]     # [0, 2, 4, 6]    — every 2nd element
lst[::-1]    # [7, 6, 5, 4, 3, 2, 1, 0]  — reversed!
```

> **Slicing never raises IndexError** — if the range goes out of bounds, Python just gives you what it can.

---

## 3. Modifying a List

```python
lst = [1, 2, 3]

# Add elements
lst.append(4)          # [1, 2, 3, 4]        — add to end, O(1)
lst.insert(0, 99)      # [99, 1, 2, 3, 4]    — insert at index 0, O(n) ← slow!
lst.extend([5, 6])     # [99, 1, 2, 3, 4, 5, 6]  — add multiple items

# Remove elements
lst.pop()              # removes and returns last element, O(1)
lst.pop(0)             # removes and returns element at index 0, O(n) ← slow!
lst.remove(3)          # removes FIRST occurrence of value 3

# Other
lst.sort()             # sorts in place, modifies the list
lst.reverse()          # reverses in place, modifies the list
sorted(lst)            # returns a NEW sorted list, original unchanged
lst.copy()             # returns a shallow copy
lst.clear()            # removes all elements → []
lst.count(2)           # how many times does 2 appear?
lst.index(2)           # index of first occurrence of 2
```

### append vs extend

```python
lst = [1, 2, 3]

lst.append([4, 5])     # [1, 2, 3, [4, 5]]  — adds the list AS ONE ELEMENT
lst.extend([4, 5])     # [1, 2, 3, 4, 5]    — adds each element individually
```

---

## 4. Iterating a List

```python
lst = [10, 20, 30]

# Basic — just the values
for val in lst:
    print(val)          # 10, 20, 30

# With index — use enumerate
for i, val in enumerate(lst):
    print(i, val)       # 0 10 / 1 20 / 2 30

# By index with range
for i in range(len(lst)):
    print(lst[i])       # 10, 20, 30

# Check membership — O(n) on lists!
10 in lst               # True
99 in lst               # False
```

---

## 5. List of Lists — What It Is

A list of lists is just a list where each element is itself a list.

```python
groups = [
    ["eat", "tea", "ate"],    # groups[0]
    ["tan", "nat"],            # groups[1]
    ["bat"],                   # groups[2]
]
```

Think of it like a **table** or **grid**:

```
groups[0]  →  ["eat", "tea", "ate"]
groups[1]  →  ["tan", "nat"]
groups[2]  →  ["bat"]
```

Or for a matrix (2D grid):

```
matrix = [
    [1, 2, 3],    # row 0
    [4, 5, 6],    # row 1
    [7, 8, 9],    # row 2
]
```

```
matrix[row][col]:

     col0  col1  col2
row0   1     2     3
row1   4     5     6
row2   7     8     9

matrix[1][2]  →  6
```

---

## 6. Creating a List of Lists

### Manual

```python
grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
```

### Building Dynamically with append

```python
result = []

result.append(["eat", "tea", "ate"])
result.append(["tan", "nat"])
result.append(["bat"])

# result = [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
```

### Building with a Loop

```python
result = []
for i in range(3):
    result.append([])      # add empty inner list
    for j in range(3):
        result[i].append(i * 3 + j)

# result = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
```

### List Comprehension (compact)

```python
# 3x3 grid of zeros
grid = [[0] * 3 for _ in range(3)]
# [[0, 0, 0],
#  [0, 0, 0],
#  [0, 0, 0]]

# ⚠️ WARNING — do NOT do this:
wrong = [[0] * 3] * 3
# Looks the same but all 3 rows point to the SAME list in memory!
wrong[0][0] = 9
# [[9, 0, 0],
#  [9, 0, 0],   ← oops, all rows changed
#  [9, 0, 0]]
```

### From dict.values() — the anagram-groups pattern

```python
from collections import defaultdict

anagram_map = defaultdict(list)
anagram_map[('a','e','t')].append("eat")
anagram_map[('a','e','t')].append("tea")
anagram_map[('a','n','t')].append("tan")

# anagram_map.values() gives:
# dict_values([["eat", "tea"], ["tan"]])

list(anagram_map.values())
# [["eat", "tea"], ["tan"]]   ← a list of lists!
```

---

## 7. Reading and Writing in a List of Lists

Use **two indices**: `lst[outer_index][inner_index]`

```python
groups = [
    ["eat", "tea", "ate"],
    ["tan", "nat"],
    ["bat"],
]

# Read
groups[0]        # ["eat", "tea", "ate"]   — the whole inner list
groups[0][1]     # "tea"                   — one element
groups[2][0]     # "bat"
groups[-1][-1]   # "bat"  — last element of last list

# Write
groups[0][0] = "EAT"     # replace a value
groups[1].append("tan2") # add to inner list
groups.append(["new"])   # add a new inner list
```

---

## 8. Iterating a List of Lists

### Outer loop only — get each inner list

```python
groups = [["eat", "tea"], ["tan", "nat"], ["bat"]]

for group in groups:
    print(group)
# ["eat", "tea"]
# ["tan", "nat"]
# ["bat"]
```

### Both loops — get each individual element

```python
for group in groups:
    for word in group:
        print(word)
# eat
# tea
# tan
# nat
# bat
```

### With indices — both row and column

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

for i, row in enumerate(matrix):
    for j, val in enumerate(row):
        print(f"[{i}][{j}] = {val}")

# [0][0] = 1
# [0][1] = 2
# ...
# [2][2] = 9
```

### Flatten (turn list of lists into one flat list)

```python
groups = [["eat", "tea"], ["tan", "nat"], ["bat"]]

# List comprehension
flat = [word for group in groups for word in group]
# ["eat", "tea", "tan", "nat", "bat"]

# Or using extend
flat = []
for group in groups:
    flat.extend(group)
```

---

## 9. Common Patterns in Interview Problems

### Return type `List[List[str]]` or `List[List[int]]`

When a problem returns `List[List[str]]`, it wants a list where each element is a list of strings.

```python
# This is the return type of groupAnagrams
-> List[List[str]]

# Valid return values:
return [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
return []                                  # empty (no groups)
return [["hello"]]                         # one group with one word
```

### Building the result list

```python
# Pattern 1: append inner lists one by one
result = []
result.append([1, 2])
result.append([3, 4])
return result   # [[1, 2], [3, 4]]

# Pattern 2: convert dict values
return list(some_dict.values())   # if values are lists

# Pattern 3: list comprehension
return [list(v) for v in some_dict.values()]
```

### Checking the inner lists

```python
groups = [["eat", "tea"], ["tan"]]

len(groups)         # 2  — number of groups
len(groups[0])      # 2  — size of first group
groups[0][0]        # "eat"  — first word of first group

# Sort each inner list (common in problems)
for group in groups:
    group.sort()

# Sort the outer list by inner list length
groups.sort(key=len)
```

---

## 10. From Your Own Solutions

### `groupAnagrams` — Full Solution Breakdown

This is the full solution, explained every single piece:

```python
from collections import defaultdict   # (1)
from typing import List               # (2)

class Solution:                       # (3)
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:  # (4)
        anagram_map = defaultdict(list)                           # (5)

        for word in strs:                                         # (6)
            sorted_key = "".join(sorted(word))                    # (7)
            anagram_map[sorted_key].append(word)                  # (8)

        return list(anagram_map.values())                         # (9)
```

---

#### Line (1) — `from collections import defaultdict`

`collections` is a built-in Python module (a file of extra tools).
`defaultdict` lives inside it, so you have to import it before using it.

```python
from collections import defaultdict
#    ^^^^^^^^^^ the module     ^^^^^^^^^^ the tool you want from it
```

Without this line, Python doesn't know what `defaultdict` means and throws a `NameError`.

---

#### Line (2) — `from typing import List`

`List` (capital L) is used only in **type hints**.
It comes from the `typing` module.

```python
from typing import List
```

This is what allows you to write `List[str]` or `List[List[str]]` in the function signature.
In Python 3.9+ you can write `list[str]` (lowercase) without importing anything — but NeetCode uses the older style so you'll see the import.

---

#### Line (3) — `class Solution:`

LeetCode/NeetCode wraps every problem in a class called `Solution`.
You don't need to think about this deeply — just know that your function always lives inside it.

```python
class Solution:        # ← the wrapper
    def yourFunction:  # ← your actual code lives indented inside
```

---

#### Line (4) — The Function Signature

```python
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
#   ^^^^^^^^^^^^^ function name
#                 ^^^^  always first in a class method, ignore it
#                       ^^^^ parameter name (the input)
#                            ^^^^^^^^^^ type hint: a list of strings
#                                                  ^^^^^^^^^^^^^^^^^ return type hint
#                                                  list of lists of strings
```

In plain English: "This function takes a list of strings and gives back a list of lists of strings."

```python
Input:  ["eat", "tea", "tan", "ate", "nat", "bat"]
Output: [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

---

#### Line (5) — `anagram_map = defaultdict(list)`

Creates a special dictionary where every new key automatically gets an empty list `[]` as its default value.

```python
anagram_map = defaultdict(list)

# What this means:
# If you access a key that doesn't exist yet, instead of a KeyError,
# Python creates that key with an empty list [] automatically.

anagram_map["abc"]           # → []   (created automatically, no error)
anagram_map["abc"].append(1) # → [1]  (appended into that auto-created list)
```

With a regular dict you'd have to write:
```python
if sorted_key not in anagram_map:
    anagram_map[sorted_key] = []
anagram_map[sorted_key].append(word)
```

`defaultdict(list)` handles that `if` check for you automatically.

---

#### Line (6) — `for word in strs:`

A standard for loop. `strs` is the input list of strings.
`word` takes the value of each string one at a time.

```python
strs = ["eat", "tea", "tan"]

# Iteration 1: word = "eat"
# Iteration 2: word = "tea"
# Iteration 3: word = "tan"
```

---

#### Line (7) — `sorted_key = "".join(sorted(word))`

This is the core idea of the whole solution. It's three functions chained together.
Read it from the **inside out**:

```python
word = "eat"

# Step 1 — sorted(word)
# sorted() takes any iterable and returns a sorted list of its characters
sorted("eat")         # ['a', 'e', 't']   ← a list of characters

# Step 2 — "".join(...)
# join() takes a list of strings and glues them together into one string
# "" means use an empty string as the separator (no space between characters)
"".join(['a', 'e', 't'])   # "aet"

# Combined:
sorted_key = "".join(sorted("eat"))   # "aet"
sorted_key = "".join(sorted("tea"))   # "aet"   ← same key!
sorted_key = "".join(sorted("ate"))   # "aet"   ← same key!
sorted_key = "".join(sorted("tan"))   # "ant"   ← different key
```

Two words that are anagrams will always produce the **same sorted key**.
This is how we group them.

```
"eat" → "aet"  ┐
"tea" → "aet"  ├── same key → same group
"ate" → "aet"  ┘
"tan" → "ant"  ┐
"nat" → "ant"  ┘── same key → same group
"bat" → "abt"  ── unique key → own group
```

---

#### Line (8) — `anagram_map[sorted_key].append(word)`

Two things happen in one line:

```python
anagram_map[sorted_key].append(word)
# ^^^^^^^^^  ^^^^^^^^^^  ^^^^^^ ^^^^
#    |           |          |    |
#    |           |          |    word = the original word ("eat")
#    |           |          append() adds word to the inner list
#    |           sorted_key = the key ("aet")
#    the defaultdict
```

Step by step:
1. `anagram_map[sorted_key]` — look up the key. If it doesn't exist yet, auto-create `[]`
2. `.append(word)` — add the original word to that list

```python
# Walking through strs = ["eat", "tea", "tan", "ate", "nat", "bat"]:

# word="eat", sorted_key="aet"
anagram_map = { "aet": ["eat"] }

# word="tea", sorted_key="aet"  (key exists, just append)
anagram_map = { "aet": ["eat", "tea"] }

# word="tan", sorted_key="ant"  (new key, auto-created)
anagram_map = { "aet": ["eat", "tea"], "ant": ["tan"] }

# word="ate", sorted_key="aet"
anagram_map = { "aet": ["eat", "tea", "ate"], "ant": ["tan"] }

# word="nat", sorted_key="ant"
anagram_map = { "aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"] }

# word="bat", sorted_key="abt"  (new key)
anagram_map = { "aet": ["eat", "tea", "ate"], "ant": ["tan", "nat"], "abt": ["bat"] }
```

---

#### Line (9) — `return list(anagram_map.values())`

```python
return list(anagram_map.values())
```

Three pieces:

```python
anagram_map.values()
# dict_values([["eat","tea","ate"], ["tan","nat"], ["bat"]])
# This is a "view" of the dict's values — not a real list yet

list(anagram_map.values())
# [["eat","tea","ate"], ["tan","nat"], ["bat"]]
# Now it's a proper list — which is what the return type List[List[str]] expects

return ...
# Sends this list of lists back to whoever called the function
```

---

### The Complete Picture

```
Input:  ["eat", "tea", "tan", "ate", "nat", "bat"]
           ↓ sorted key for each word
         "aet" "aet" "ant" "aet" "ant" "abt"
           ↓ grouped by key in defaultdict
         {
           "aet": ["eat", "tea", "ate"],
           "ant": ["tan", "nat"],
           "abt": ["bat"]
         }
           ↓ .values() → list()
Output: [["eat","tea","ate"], ["tan","nat"], ["bat"]]
```

**Time complexity:** O(n × k log k) — n words, each sorted in k log k (k = word length)
**Space complexity:** O(n × k) — storing all characters across all words

---

## Quick Reference

```python
# CREATE
lst = []                         # empty
lst = [1, 2, 3]                  # literal
lst = [[1,2], [3,4]]             # list of lists
lst = [[0]*cols for _ in range(rows)]  # 2D grid

# ACCESS
lst[i]           # single element
lst[i][j]        # element in list of lists
lst[-1]          # last element
lst[1:4]         # slice (indices 1, 2, 3)

# MODIFY
lst.append(x)        # add to end
lst.extend([x,y])    # add multiple items
lst.pop()            # remove + return last
lst[i] = x           # overwrite at index i

# ITERATE
for val in lst:                       # values
for i, val in enumerate(lst):         # index + value
for row in matrix:                    # outer list
for row in matrix: for val in row:    # all elements
```
