# Stacks

> **NeetCode Stack problems:** Valid Parentheses · Min Stack · Evaluate Reverse Polish Notation · Daily Temperatures · Car Fleet · Largest Rectangle In Histogram

---

## Table of Contents

1. [What is a Stack?](#1-what-is-a-stack)
2. [Stack in Python](#2-stack-in-python)
3. [The Two Stack Patterns](#3-the-two-stack-patterns)
4. [Pattern A — Matching / Validation](#pattern-a--matching--validation)
5. [Pattern B — Monotonic Stack](#pattern-b--monotonic-stack)
6. [Problem Walkthroughs](#6-problem-walkthroughs)

---

## 1. What is a Stack?

A stack is a collection where the **last item added is the first item removed**.
Think of a stack of plates — you add to the top, you take from the top.

```
Push 1 → [1]
Push 2 → [1, 2]
Push 3 → [1, 2, 3]
Pop    → returns 3, stack is [1, 2]
Pop    → returns 2, stack is [1]
Peek   → returns 1 (without removing)
```

**LIFO = Last In, First Out**

The question a stack answers is always:
> *"What was the most recent thing I haven't dealt with yet?"*

---

## 2. Stack in Python

Python does **not** have a dedicated Stack class. You use a regular **list**.

```python
stack = []

# Push — add to top
stack.append(x)       # O(1)

# Pop — remove from top
stack.pop()           # O(1) — returns the removed value
                      # raises IndexError if stack is empty!

# Peek — look at top without removing
stack[-1]             # O(1) — raises IndexError if empty

# Safe peek
stack[-1] if stack else None

# Check if empty
len(stack) == 0
not stack             # same thing — empty list is falsy

# Size
len(stack)
```

### Common Safe Pattern

```python
# Always check before popping or peeking
if stack:
    val = stack.pop()

# Or in one line with guard
while stack and condition:
    stack.pop()
```

---

## 3. The Two Stack Patterns

Almost every stack problem is one of these two:

| Pattern | Question being asked | Problems |
|---|---|---|
| **Matching / Validation** | Does this open thing have a matching close? | Valid Parentheses |
| **Monotonic Stack** | What is the next greater/smaller element? | Daily Temperatures, Car Fleet, Largest Rectangle |

Min Stack and Evaluate Reverse Polish Notation are their own variants (explained below).

---

## Pattern A — Matching / Validation

**Idea:** Push opening items onto the stack. When you see a closing item, check if it matches the most recent opening item (the top of the stack).

```
Input: "({[]})"

See '('  → push  → stack: ['(']
See '{'  → push  → stack: ['(', '{']
See '['  → push  → stack: ['(', '{', '[']
See ']'  → pop '[', does ']' match '['? YES → stack: ['(', '{']
See '}'  → pop '{', does '}' match '{'? YES → stack: ['(']
See ')'  → pop '(', does ')' match '('? YES → stack: []
Stack is empty at the end → VALID ✓
```

```
Input: "([)]"

See '('  → push  → stack: ['(']
See '['  → push  → stack: ['(', '[']
See ')'  → pop '[', does ')' match '['? NO → INVALID ✗
```

**Template:**

```python
stack = []
for char in s:
    if is_opening(char):
        stack.append(char)
    else:  # it's a closing char
        if not stack:
            return False          # nothing to match with
        top = stack.pop()
        if not matches(top, char):
            return False
return len(stack) == 0            # must be empty at the end
```

---

## Pattern B — Monotonic Stack

**Idea:** Maintain a stack that is always sorted (either always increasing or always decreasing).
When a new element violates the order, pop and process elements until order is restored.

**Monotonic increasing stack** — stack goes low → high from bottom to top.
Each element is popped when something *smaller* arrives.
→ Used for "next smaller element" problems.

**Monotonic decreasing stack** — stack goes high → low from bottom to top.
Each element is popped when something *larger* arrives.
→ Used for "next greater element" problems (like Daily Temperatures).

```
Daily Temperatures: [73, 74, 75, 71, 69, 72, 76, 73]
Goal: for each day, how many days until a warmer day?

Keep a stack of indices whose temperature hasn't been "answered" yet.
Pop an index when we find a temperature warmer than it.

i=0, temp=73 → stack empty, push 0       → stack: [0]
i=1, temp=74 → 74>73, pop 0: ans[0]=1-0=1, push 1  → stack: [1]
i=2, temp=75 → 75>74, pop 1: ans[1]=2-1=1, push 2  → stack: [2]
i=3, temp=71 → 71<75, push 3            → stack: [2,3]
i=4, temp=69 → 69<71, push 4            → stack: [2,3,4]
i=5, temp=72 → 72>69, pop 4: ans[4]=5-4=1
             → 72>71, pop 3: ans[3]=5-3=2
             → 72<75, push 5            → stack: [2,5]
i=6, temp=76 → 76>72, pop 5: ans[5]=6-5=1
             → 76>75, pop 2: ans[2]=6-2=4
             → stack empty, push 6      → stack: [6]
i=7, temp=73 → 73<76, push 7            → stack: [6,7]

Remaining in stack → 0 (no warmer day found)
ans = [1, 1, 4, 2, 1, 1, 0, 0]
```

**Template:**

```python
stack = []   # stores indices
result = [0] * len(nums)

for i in range(len(nums)):
    while stack and nums[i] > nums[stack[-1]]:   # new element beats top
        idx = stack.pop()
        result[idx] = i - idx                     # distance to answer
    stack.append(i)

return result
```

---

## 6. Problem Walkthroughs

---

### Valid Parentheses (Easy)

**Problem:** Given a string of `(`, `)`, `{`, `}`, `[`, `]` — is it valid?
Valid means every opening bracket has a matching closing bracket in the right order.

**Pattern:** Matching / Validation

```python
def isValid(self, s: str) -> bool:
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    #        closing → its expected opening

    for char in s:
        if char in pairs:                    # it's a closing bracket
            if not stack or stack[-1] != pairs[char]:
                return False                 # nothing to match, or wrong match
            stack.pop()                      # matched — remove the opening
        else:
            stack.append(char)               # it's an opening bracket — push it

    return len(stack) == 0                   # valid only if nothing left unmatched
```

**Trace with `"()[]{}":`**
```
'(' → not closing → push   → stack: ['(']
')' → closing, pairs[')']='(' → stack[-1]='(' ✓ → pop  → stack: []
'[' → push   → stack: ['[']
']' → pairs[']']='[' → stack[-1]='[' ✓ → pop  → stack: []
'{' → push   → stack: ['{']
'}' → pairs['}]='{' → stack[-1]='{' ✓ → pop  → stack: []
return len([]) == 0 → True ✓
```

**Key trick:** Store closing→opening in a dict. When you see a closing bracket, just look up what its opening partner should be, and check against the stack top.

---

### Min Stack (Medium)

**Problem:** Design a stack that supports `push`, `pop`, `top`, and `getMin` — all in O(1).

**The challenge:** `pop` can remove the current minimum, so you can't just store one min value.

**Pattern:** Store the minimum *at the time of each push* alongside the value.

```python
class MinStack:
    def __init__(self):
        self.stack = []
        # Each entry is [value, min_at_time_of_push]

    def push(self, val: int) -> None:
        current_min = min(val, self.stack[-1][1] if self.stack else val)
        self.stack.append([val, current_min])

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]    # min is always stored at the top
```

**Trace:**
```
push(5)  → stack: [[5, 5]]            min so far: 5
push(3)  → stack: [[5,5],[3,3]]       min so far: 3
push(7)  → stack: [[5,5],[3,3],[7,3]] min so far: 3 (still)
getMin() → stack[-1][1] = 3 ✓
pop()    → stack: [[5,5],[3,3]]
getMin() → stack[-1][1] = 3 ✓
pop()    → stack: [[5,5]]
getMin() → stack[-1][1] = 5 ✓
```

**Key insight:** Each element "remembers" what the minimum was when it was pushed.
When you pop, the new top already knows the correct minimum for what remains.

---

### Evaluate Reverse Polish Notation (Medium)

**Problem:** Evaluate an arithmetic expression in Reverse Polish Notation (postfix).
Tokens are numbers or operators (`+`, `-`, `*`, `/`).

**What is RPN?**
```
Normal:  3 + 4       → infix (operator in the middle)
RPN:     3 4 +       → postfix (operator comes after operands)

"2 1 + 3 *"  means  (2 + 1) * 3 = 9
```

**Pattern:** Numbers go on the stack. When you see an operator, pop two numbers, apply the operator, push the result.

```python
def evalRPN(self, tokens: List[str]) -> int:
    stack = []

    for token in tokens:
        if token in {'+', '-', '*', '/'}:
            b = stack.pop()     # second operand (popped first)
            a = stack.pop()     # first operand

            if token == '+': stack.append(a + b)
            elif token == '-': stack.append(a - b)
            elif token == '*': stack.append(a * b)
            elif token == '/': stack.append(int(a / b))  # truncate toward zero
        else:
            stack.append(int(token))   # it's a number — push it

    return stack[0]    # one number remains — the result
```

**Trace `["2","1","+","3","*"]`:**
```
"2"  → push 2    → stack: [2]
"1"  → push 1    → stack: [2, 1]
"+"  → pop 1, pop 2, push 2+1=3  → stack: [3]
"3"  → push 3    → stack: [3, 3]
"*"  → pop 3, pop 3, push 3*3=9  → stack: [9]
return 9 ✓
```

**Note on division:** `int(a / b)` truncates toward zero.
Python's `//` operator floors (rounds toward negative infinity), which is different for negative numbers:
```python
int(-7 / 2)   # -3   (truncate toward zero — correct for this problem)
-7 // 2       # -4   (floor — WRONG for this problem)
```

---

### Daily Temperatures (Medium)

**Problem:** Given temperatures, return an array where each element is the number of days until a warmer temperature. If no warmer day exists, use 0.

**Pattern:** Monotonic decreasing stack (stores indices, not temperatures)

```python
def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
    result = [0] * len(temperatures)
    stack = []   # stores indices of "unanswered" days

    for i, temp in enumerate(temperatures):
        while stack and temp > temperatures[stack[-1]]:
            idx = stack.pop()               # this day now has an answer
            result[idx] = i - idx           # days waited = current index - that index
        stack.append(i)

    return result
    # anything remaining in stack → result stays 0 (no warmer day)
```

---

### Car Fleet (Medium)

**Problem:** Cars drive toward a target. Each car has a position and speed.
A car that catches up to one ahead joins its fleet and slows to the leader's speed.
Return the number of fleets that arrive at the target.

**Key insight:** Sort by starting position (closest to target first).
Calculate each car's time to reach the target.
If a car behind takes *less or equal* time than the car ahead → it catches up → same fleet.
If it takes *more* time → it can never catch up → new fleet.

**Pattern:** Stack of arrival times. If current time ≤ top of stack, it merges (pop and discard). Otherwise push new fleet time.

```python
def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
    # Pair positions with speeds, sort by position descending (closest to target first)
    cars = sorted(zip(position, speed), reverse=True)
    stack = []   # stores arrival times of fleets

    for pos, spd in cars:
        time = (target - pos) / spd     # time for this car to reach target

        if not stack or time > stack[-1]:
            stack.append(time)          # new fleet — takes longer than the one ahead
        # if time <= stack[-1]: this car catches up, joins the fleet ahead (don't push)

    return len(stack)
```

---

### Largest Rectangle In Histogram (Hard)

**Problem:** Given bar heights in a histogram, find the largest rectangle you can form.

**Pattern:** Monotonic increasing stack. When a shorter bar arrives, it limits the height of previous bars. Pop and calculate area for each popped bar.

```python
def largestRectangleArea(self, heights: List[int]) -> int:
    stack = []    # stores (index, height) pairs
    max_area = 0

    for i, h in enumerate(heights):
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            # This bar can now only extend to current index i
            area = height * (i - idx)
            max_area = max(max_area, area)
            start = idx    # the new bar can extend back to where this one started

        stack.append((start, h))

    # Any bars still in stack extend all the way to the end
    for idx, height in stack:
        area = height * (len(heights) - idx)
        max_area = max(max_area, area)

    return max_area
```

---

## Quick Reference — Stacks

```python
# Setup
stack = []

# Operations
stack.append(x)          # push — O(1)
stack.pop()              # pop top — O(1)
stack[-1]                # peek — O(1)
not stack                # check if empty
len(stack)               # size

# Safe pop
if stack:
    val = stack.pop()

# Pattern A: Matching
for char in s:
    if opening: stack.append(char)
    else:
        if not stack or stack[-1] != expected: return False
        stack.pop()
return not stack

# Pattern B: Monotonic (next greater)
for i, val in enumerate(nums):
    while stack and val > nums[stack[-1]]:
        idx = stack.pop()
        result[idx] = i - idx
    stack.append(i)
```

## Complexity

All basic stack operations are **O(1)**.
Monotonic stack problems are **O(n)** overall — each element is pushed and popped at most once.
