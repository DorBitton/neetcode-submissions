# My Progress Analysis

_Last updated: June 2026_

---

## Problems Solved

### Python For Beginners (7/7 complete)
- hello-world, printing-text, variable-declaration, comments, execution-order, code-errors, what-is-python

### Data Structures & Algorithms
| Problem | Category | Approach | Notes |
|---|---|---|---|
| duplicate-integer | Arrays & Hashing | Set, O(n) | Clean, optimal |
| is-anagram | Arrays & Hashing | Counter / manual dict | Did it two ways — good |
| two-integer-sum | Arrays & Hashing | Hash map, O(n) | Optimal one-pass |
| anagram-groups | Arrays & Hashing | Sorted key + defaultdict | Improved on 2nd try |

---

## Key Insight From My Solutions

**Every single DS&A problem I solved uses a hash map or set.**
This is the core of the "Arrays & Hashing" pattern:
> Instead of nested loops (O(n²)), store values in a hash map/set for O(1) lookup → total O(n).

I already understand the most important trade-off in interview problems: **spend extra space (O(n)) to save time**.

---

## Patterns I Know

- [x] **Hash Set** — for checking membership/duplicates in O(1)
- [x] **Hash Map** — for storing value → index or value → count
- [x] **Sorted string as dict key** — for grouping anagrams
- [x] **Counter** — Python shortcut for character frequency maps
- [x] **defaultdict** — cleaner dict with default values

---

## Python Tools I've Used

```python
# Set for O(1) lookup
seen = set()
seen.add(x)
x in seen          # O(1)

# Hash map pattern (Two Sum)
seen = {}
seen[num] = index
complement in seen # O(1)

# Counter (character frequency)
from collections import Counter
Counter("hello")   # {'l': 2, 'h': 1, 'e': 1, 'o': 1}

# defaultdict (no KeyError on missing key)
from collections import defaultdict
d = defaultdict(list)
d["key"].append("value")  # no need to check if key exists

# enumerate (index + value together)
for i, val in enumerate(nums):
    ...

# sorted + tuple as dict key
key = tuple(sorted(word))  # "eat" → ('a', 'e', 't')
```

---

## Things to Watch Out For

- **Remove debug prints before submitting** — found a leftover `print(key)` in anagram-groups submission-0.
- **Distinguish Counter (convenient) from manual dict (educational)** — know both, use whichever is clearer.

---

## What's Next

I've finished **Arrays & Hashing**. The NeetCode roadmap continues:

1. **Two Pointers** — left/right pointers moving toward each other or same direction
2. **Sliding Window** — a subarray that "slides" through the input
3. **Stack** — LIFO structure for matching/nesting problems
4. **Binary Search** — O(log n) search on sorted data

**Recommended first problem for Two Pointers:** `valid-palindrome`
