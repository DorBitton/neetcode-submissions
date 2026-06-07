# Interview Patterns

Recognizing the pattern is the real skill. Once you see it, the solution follows.

> **Completed:** Arrays & Hashing
> **Next up:** Two Pointers

---

## Pattern 1 — Arrays & Hashing ✓

**The idea:** Use a hash map or set to avoid slow nested loops.
Trade O(n) extra space to get O(n) time instead of O(n²).

**Recognize it when:**
- "Does this array contain a duplicate?"
- "Find two elements that sum to X"
- "Group these strings by some property"
- "How many times does each element appear?"

**Template:**

```python
# Membership check (set)
seen = set()
for x in nums:
    if x in seen:       # O(1) check
        # found it
    seen.add(x)

# Value → index (dict)
seen = {}
for i, x in enumerate(nums):
    if something in seen:
        return [seen[something], i]
    seen[x] = i

# Frequency count
count = {}
for x in items:
    count[x] = count.get(x, 0) + 1
# or:
from collections import Counter
count = Counter(items)

# Grouping
from collections import defaultdict
groups = defaultdict(list)
for x in items:
    key = transform(x)      # e.g. sorted chars, first letter
    groups[key].append(x)
return list(groups.values())
```

**Your solved problems using this pattern:**
- `duplicate-integer` → set membership
- `two-integer-sum` → dict value→index
- `is-anagram` → Counter comparison
- `anagram-groups` → defaultdict grouping

---

## Pattern 2 — Two Pointers

**The idea:** Use two index variables (left and right, or slow and fast) moving through the input.
Avoids nested loops. Usually O(n) time, O(1) extra space.

**Recognize it when:**
- "Is this a palindrome?"
- "Find a pair with sum X in a sorted array"
- "Remove duplicates in place"
- "Reverse something"

**Template:**

```python
# Left/right closing in
left, right = 0, len(nums) - 1
while left < right:
    if condition:
        return something
    elif nums[left] + nums[right] < target:
        left += 1
    else:
        right -= 1

# Same direction (slow/fast)
slow = 0
for fast in range(len(nums)):
    if condition:
        nums[slow] = nums[fast]
        slow += 1
```

---

## Pattern 3 — Sliding Window

**The idea:** Maintain a "window" (subarray or substring) that slides through the input.
Grow the window by moving right pointer, shrink by moving left pointer.

**Recognize it when:**
- "Longest/shortest subarray that satisfies X"
- "Substring with certain characters"
- "Maximum sum subarray of size k"

**Template:**

```python
# Variable-size window
left = 0
for right in range(len(s)):
    # add s[right] to window

    while window_is_invalid:
        # remove s[left] from window
        left += 1

    # update answer using current window size: right - left + 1
```

---

## Pattern 4 — Stack

**The idea:** Push items onto a stack, pop when a condition is met.
Useful for matching pairs or "what was the last thing I saw?"

**Recognize it when:**
- "Valid parentheses / brackets"
- "Next greater element"
- "Evaluate an expression"

**Template:**

```python
stack = []
for x in items:
    while stack and condition(stack[-1], x):
        stack.pop()
        # process the popped element
    stack.append(x)
```

---

## Pattern 5 — Binary Search

**The idea:** On a sorted input, eliminate half the possibilities each step.
O(log n) instead of O(n).

**Recognize it when:**
- Input is sorted (or can be treated as sorted)
- "Find target in sorted array"
- "Find minimum/maximum that satisfies a condition"

**Template:**

```python
left, right = 0, len(nums) - 1
while left <= right:
    mid = (left + right) // 2
    if nums[mid] == target:
        return mid
    elif nums[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
return -1   # not found
```

---

## How to Identify the Pattern (Quick Guide)

| Clue in the problem | Likely pattern |
|---|---|
| "duplicate", "seen before", "unique" | Set / Hash Map |
| "two numbers sum to target" | Hash Map |
| "group by", "anagram", "frequency" | Hash Map / Counter |
| "palindrome", "pair in sorted array" | Two Pointers |
| "longest/shortest subarray/substring" | Sliding Window |
| "brackets", "matching pairs" | Stack |
| "sorted array", "find target efficiently" | Binary Search |
| "shortest path", "level by level" | BFS |
| "all possibilities", "combinations" | DFS / Backtracking |
