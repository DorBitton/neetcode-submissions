# Data Structures

Quick guide to each structure — what it is, how to use it in Python, when to reach for it.

> For deeper coverage of Set, Dict, defaultdict, Counter → see [`sets-and-hashmaps.md`](./sets-and-hashmaps.md)
> For deeper coverage of List and nested lists → see [`../python-basics/lists-and-nested-lists.md`](../python-basics/lists-and-nested-lists.md)

---

## Covered So Far

- [x] List / Array
- [x] Hash Set (`set`)
- [x] Hash Map (`dict`, `defaultdict`, `Counter`)
- [x] Tuple

## Still to Learn

- [ ] Stack
- [ ] Queue / Deque
- [ ] Linked List
- [ ] Binary Tree
- [ ] Heap / Priority Queue
- [ ] Graph

---

## List / Array

Ordered, mutable sequence. The default go-to structure.

```python
lst = [1, 2, 3]
lst.append(x)       # O(1)
lst[i]              # O(1)
x in lst            # O(n) — use set for fast lookup
lst.sort()          # O(n log n)
```

Full notes: [`../python-basics/lists-and-nested-lists.md`](../python-basics/lists-and-nested-lists.md)

---

## Hash Set

Unordered collection of unique values. Backed by a hash table.

```python
s = set()
s.add(x)        # O(1)
x in s          # O(1) ← this is the whole point
s.discard(x)    # O(1), no error if missing
```

**Use when:** "Have I seen this before?" or "Remove duplicates."

Full notes: [`sets-and-hashmaps.md`](./sets-and-hashmaps.md)

---

## Hash Map

Maps keys to values. Keys must be hashable (str, int, tuple — NOT list).

```python
d = {}
d[key] = val         # O(1)
d.get(key, default)  # O(1), safe
key in d             # O(1) key check
for k, v in d.items(): ...
```

**Use when:** You need to associate a value with a key (e.g. value → index, char → count).

Full notes: [`sets-and-hashmaps.md`](./sets-and-hashmaps.md)

---

## defaultdict

A dict that auto-creates a default value for missing keys.

```python
from collections import defaultdict
d = defaultdict(list)   # missing key → []
d = defaultdict(int)    # missing key → 0
d[key].append(item)     # no KeyError
```

**Use when:** Grouping items by a key.

---

## Counter

A dict specialized for counting. Missing keys return 0.

```python
from collections import Counter
c = Counter(iterable)
c["x"]           # count of "x", 0 if missing
Counter(s) == Counter(t)  # compare frequencies
```

**Use when:** Counting character or element frequencies.

---

## Tuple

Immutable ordered sequence. Because it cannot change, it is **hashable**.

```python
t = (1, 2, 3)
t = tuple(sorted("eat"))   # ('a', 'e', 't')

t[0]         # access — O(1)
x in t       # O(n) — same as list
len(t)
```

**Key use in interviews:**
```python
# Tuples can be dict keys — lists CANNOT
d[tuple(sorted(word))] = ...   # valid ✓
d[sorted(word)] = ...          # TypeError — list is not hashable ✗
```

**Use when:** You need an immutable version of a list, especially as a dict key.

---

## Stack

Last-In, First-Out (LIFO). Use a Python list.

```python
stack = []
stack.append(x)   # push — O(1)
stack.pop()       # pop from top — O(1)
stack[-1]         # peek at top — O(1)
len(stack) == 0   # check if empty
```

**Use when:** Matching brackets, undo operations, DFS.

---

## Queue / Deque

First-In, First-Out (FIFO). Use `collections.deque`.

```python
from collections import deque
q = deque()
q.append(x)       # enqueue (add to right) — O(1)
q.popleft()       # dequeue (remove from left) — O(1)
# DO NOT use list.pop(0) for a queue — it's O(n)
```

**Use when:** BFS, processing items in order.

---

## Heap / Priority Queue

Gives you the smallest (or largest) element in O(log n).
Python's `heapq` is a **min-heap** by default.

```python
import heapq
heap = []
heapq.heappush(heap, val)   # add — O(log n)
heapq.heappop(heap)         # remove + return min — O(log n)
heap[0]                     # peek at min — O(1)

# Max-heap trick: negate the values
heapq.heappush(heap, -val)
-heapq.heappop(heap)        # negate back to get original

# From a list
heapq.heapify(lst)          # convert list to heap in O(n)
```

**Use when:** "Find the k largest/smallest", "always process the minimum next."
