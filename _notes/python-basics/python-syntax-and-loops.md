# Python Syntax, For Loops & Return Types — Complete Guide

> Read this before going back to the hash map notes.
> Everything here is things you'll use in every single interview problem.

---

## Table of Contents

1. [How Python Code is Structured](#1-how-python-code-is-structured)
2. [Variables and Types](#2-variables-and-types)
3. [Functions — def, parameters, return](#3-functions--def-parameters-return)
4. [Return Types and Type Hints](#4-return-types-and-type-hints)
5. [For Loops — Every Form](#5-for-loops--every-form)
6. [While Loops](#6-while-loops)
7. [If / Elif / Else](#7-if--elif--else)
8. [Useful Built-in Functions](#8-useful-built-in-functions)
9. [Reading Interview Problem Code](#9-reading-interview-problem-code)

---

## 1. How Python Code is Structured

Python uses **indentation** (spaces) instead of `{}` braces to define blocks.
This is the #1 source of confusion for beginners.

```python
# Everything at the same indentation level belongs to the same block

def my_function():          # function starts here
    x = 10                  # inside the function (indented)
    if x > 5:               # if statement inside the function
        print("big")        # inside the if (double indented)
    print("done")           # back to function level (single indent)

print("outside")            # outside the function (no indent)
```

**Rules:**
- Use **4 spaces** per level (standard in Python)
- Tabs and spaces cannot be mixed — pick one (use spaces)
- A `:` at the end of a line always starts a new indented block

```python
# These all end with : and start a new block:
def foo():
for x in items:
while condition:
if condition:
elif condition:
else:
class MyClass:
```

---

## 2. Variables and Types

Python is **dynamically typed** — you don't declare the type, Python figures it out.

```python
# Basic types
x = 5           # int
y = 3.14        # float
name = "Alice"  # str
flag = True     # bool  (capital T and F!)
nothing = None  # NoneType  — Python's version of null/nil

# You can check the type
type(x)         # <class 'int'>
type(name)      # <class 'str'>
```

### Type Conversion (Casting)

```python
int("42")       # 42      — string to int
str(42)         # "42"    — int to string
float("3.14")   # 3.14    — string to float
int(3.9)        # 3       — float to int (truncates, does NOT round)
bool(0)         # False
bool(1)         # True
bool("")        # False   — empty string is falsy
bool("hi")      # True    — non-empty string is truthy
```

### Falsy Values — Important for Interview Code

These all behave like `False` in an `if` statement:

```python
False
None
0
0.0
""        # empty string
[]        # empty list
{}        # empty dict
set()     # empty set
```

```python
# This pattern is common in interviews:
if not result:       # same as: if result == [] or result == "" or result is None
    return []
```

---

## 3. Functions — def, parameters, return

### Basic Function

```python
def greet():             # define a function named greet
    print("Hello!")      # body of the function

greet()                  # call the function → prints "Hello!"
```

### Function with Parameters

```python
def add(a, b):           # a and b are parameters (inputs)
    return a + b         # return sends a value back to the caller

result = add(3, 4)       # call with arguments 3 and 4
print(result)            # 7
```

### Parameters vs Arguments

```python
def add(a, b):    # a and b are PARAMETERS (variable names in definition)
    return a + b

add(3, 4)         # 3 and 4 are ARGUMENTS (actual values passed in)
```

### Default Parameter Values

```python
def greet(name, greeting="Hello"):    # greeting has a default
    print(f"{greeting}, {name}!")

greet("Alice")              # Hello, Alice!
greet("Alice", "Hey")       # Hey, Alice!
```

### Multiple Return Values

Python can return multiple values as a tuple:

```python
def min_max(nums):
    return min(nums), max(nums)     # returns a tuple

low, high = min_max([3, 1, 4, 1, 5])   # unpack the tuple
print(low)   # 1
print(high)  # 5
```

### The `return` Statement

```python
def find_first(nums, target):
    for i, num in enumerate(nums):
        if num == target:
            return i        # exits the function immediately
    return -1               # only reaches here if target was never found

# A function with no return statement returns None automatically
def say_hi():
    print("hi")

result = say_hi()
print(result)   # None
```

---

## 4. Return Types and Type Hints

In interview problems (like on NeetCode/LeetCode), you'll see this syntax:

```python
def twoSum(self, nums: List[int], target: int) -> List[int]:
```

This looks scary but it's just **type hints** — annotations that tell you what types go in and come out. Python doesn't enforce them, they're just documentation.

### Breaking It Down

```python
def twoSum(self, nums: List[int], target: int) -> List[int]:
#          ^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^
#          |     parameters with type hints     return type hint
#          |
#          "self" means this is a class method (explained below)
```

| Syntax | Meaning |
|---|---|
| `x: int` | x is an integer |
| `x: str` | x is a string |
| `x: float` | x is a float |
| `x: bool` | x is a boolean |
| `x: List[int]` | x is a list of integers |
| `x: List[str]` | x is a list of strings |
| `x: Dict[str, int]` | x is a dict mapping strings to ints |
| `x: Optional[int]` | x is an int OR None |
| `-> int` | this function returns an int |
| `-> List[int]` | this function returns a list of ints |
| `-> None` | this function returns nothing |
| `-> bool` | this function returns True or False |

### Common Examples from Interview Problems

```python
# Returns a boolean
def hasDuplicate(self, nums: List[int]) -> bool:
    ...

# Takes a string, returns a boolean
def isAnagram(self, s: str, t: str) -> bool:
    ...

# Takes a list of strings, returns a list of lists of strings
def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
    ...

# Takes a list and a target, returns a list of two ints
def twoSum(self, nums: List[int], target: int) -> List[int]:
    ...
```

### What is `self`?

```python
class Solution:
    def twoSum(self, nums, target):
        ...
```

NeetCode/LeetCode wrap every solution in a `class Solution:`.
`self` refers to the instance of the class — you can basically ignore it for now.
Just know that it's always the first parameter in a class method.

```python
# You write this:
class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        seen = set()
        for num in nums:
            if num in seen:
                return True
            seen.add(num)
        return False

# The judge calls it like this (you don't write this part):
sol = Solution()
sol.hasDuplicate([1, 2, 3, 1])  # True
```

---

## 5. For Loops — Every Form

### Basic For Loop — Iterating Over a List

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)

# apple
# banana
# cherry
```

`fruit` is just a variable name — it takes the value of each element in turn.
You can name it anything: `for x in fruits`, `for item in fruits`, etc.

### For Loop Over a String

```python
for char in "hello":
    print(char)

# h
# e
# l
# l
# o
```

A string is iterable — Python loops through each character.

### For Loop with `range()`

`range()` generates a sequence of numbers.

```python
for i in range(5):
    print(i)
# 0, 1, 2, 3, 4   (starts at 0, stops BEFORE 5)

for i in range(2, 6):
    print(i)
# 2, 3, 4, 5   (starts at 2, stops BEFORE 6)

for i in range(0, 10, 2):
    print(i)
# 0, 2, 4, 6, 8   (start, stop, step)

for i in range(5, 0, -1):
    print(i)
# 5, 4, 3, 2, 1   (count down)
```

### For Loop with Index — `enumerate()`

When you need both the index AND the value:

```python
fruits = ["apple", "banana", "cherry"]

# Without enumerate — awkward
for i in range(len(fruits)):
    print(i, fruits[i])

# With enumerate — clean
for i, fruit in enumerate(fruits):
    print(i, fruit)

# 0 apple
# 1 banana
# 2 cherry
```

`enumerate(fruits)` produces pairs: `(0, "apple"), (1, "banana"), (2, "cherry")`
You unpack each pair into `i` and `fruit`.

```python
# You can also start counting from a different number:
for i, fruit in enumerate(fruits, start=1):
    print(i, fruit)
# 1 apple
# 2 banana
# 3 cherry
```

### For Loop Over a Dict

```python
d = {"a": 1, "b": 2, "c": 3}

# Keys only (default)
for key in d:
    print(key)        # a, b, c

# Values only
for val in d.values():
    print(val)        # 1, 2, 3

# Keys and values together — most common in interviews
for key, val in d.items():
    print(key, val)   # a 1 / b 2 / c 3
```

### Nested For Loops

```python
matrix = [[1, 2, 3],
          [4, 5, 6],
          [7, 8, 9]]

for row in matrix:
    for val in row:
        print(val)
# 1 2 3 4 5 6 7 8 9

# With indices:
for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        print(f"matrix[{i}][{j}] = {matrix[i][j]}")
```

### `break` and `continue`

```python
# break — exit the loop immediately
for i in range(10):
    if i == 5:
        break
    print(i)
# 0, 1, 2, 3, 4

# continue — skip the rest of this iteration, go to next
for i in range(10):
    if i % 2 == 0:
        continue     # skip even numbers
    print(i)
# 1, 3, 5, 7, 9
```

### `for` with `else`

Python has a unique feature: `else` on a for loop runs if the loop completed WITHOUT a `break`.

```python
def find_target(nums, target):
    for num in nums:
        if num == target:
            print("Found!")
            break
    else:
        print("Not found")    # only runs if loop never broke

find_target([1, 2, 3], 2)    # Found!
find_target([1, 2, 3], 99)   # Not found
```

### List Comprehension — Compact For Loop

Very common in Python, you'll see this in solutions:

```python
# Regular loop to build a list
squares = []
for x in range(5):
    squares.append(x ** 2)
# [0, 1, 4, 9, 16]

# Same thing as a list comprehension
squares = [x ** 2 for x in range(5)]
# [0, 1, 4, 9, 16]

# With a condition (filter)
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]

# Nested (flattening a matrix)
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [val for row in matrix for val in row]
# [1, 2, 3, 4, 5, 6]
```

---

## 6. While Loops

Run as long as a condition is true.

```python
i = 0
while i < 5:
    print(i)
    i += 1
# 0, 1, 2, 3, 4

# Infinite loop with manual break
while True:
    user_input = input("Enter 'quit' to stop: ")
    if user_input == "quit":
        break
```

### Two Pointers Pattern (uses while loop)

```python
# Classic two-pointer setup — you'll use this in the next NeetCode section
left = 0
right = len(nums) - 1

while left < right:
    # do something
    left += 1
    right -= 1
```

---

## 7. If / Elif / Else

```python
x = 15

if x > 20:
    print("big")
elif x > 10:      # "else if"
    print("medium")   # ← this runs
elif x > 5:
    print("small")
else:
    print("tiny")
```

### Comparison Operators

```python
x == y    # equal
x != y    # not equal
x > y     # greater than
x >= y    # greater than or equal
x < y     # less than
x <= y    # less than or equal

x is y    # same object in memory (use for None: x is None)
x is not y
```

### Logical Operators

```python
x > 0 and x < 10    # both must be true
x < 0 or x > 10     # at least one must be true
not (x > 0)         # invert

# Python shortcut for range check:
0 < x < 10          # same as x > 0 and x < 10
```

### Ternary (One-Line If)

```python
# Regular
if x > 0:
    label = "positive"
else:
    label = "non-positive"

# Same thing in one line
label = "positive" if x > 0 else "non-positive"
```

---

## 8. Useful Built-in Functions

These come up constantly in interview solutions:

```python
len([1, 2, 3])           # 3 — length of any sequence
min([3, 1, 2])           # 1
max([3, 1, 2])           # 3
sum([1, 2, 3])           # 6
abs(-5)                  # 5 — absolute value
sorted([3, 1, 2])        # [1, 2, 3] — returns new sorted list
sorted([3, 1, 2], reverse=True)  # [3, 2, 1]

range(5)                 # 0, 1, 2, 3, 4
list(range(5))           # [0, 1, 2, 3, 4]

zip([1,2,3], ["a","b","c"])          # pairs: (1,"a"), (2,"b"), (3,"c")
list(zip([1,2,3], ["a","b","c"]))    # [(1,"a"), (2,"b"), (3,"c")]

enumerate(["a","b","c"])             # (0,"a"), (1,"b"), (2,"c")

any([False, False, True])  # True  — is at least one element truthy?
all([True, True, True])    # True  — are ALL elements truthy?
all([True, False, True])   # False

# String operations
"hello".upper()          # "HELLO"
"HELLO".lower()          # "hello"
"hello world".split()    # ["hello", "world"]
" hello ".strip()        # "hello"  — removes whitespace
"".join(["a", "b", "c"]) # "abc"   — join list into string
",".join(["a", "b", "c"])# "a,b,c"

# Type checks
isinstance(x, int)       # True if x is an int
isinstance(x, (int, float))  # True if x is int OR float
```

---

## 9. Reading Interview Problem Code

Now that you know the syntax, let's fully decode your own solutions.

### `duplicate-integer` — Line by Line

```python
class Solution:                          # wrapper class (ignore for now)
    def hasDuplicate(self,               # method definition
                     nums: List[int]     # parameter: list of ints
                    ) -> bool:           # return type: True or False

        seen = set()                     # create empty set

        for num in nums:                 # loop: num takes each value in nums
            if num in seen:              # O(1) check: was num seen before?
                return True             # yes → duplicate found, exit now
            seen.add(num)               # no → remember this number

        return False                     # loop finished, no duplicate found
```

### `two-integer-sum` — Line by Line

```python
class Solution:
    def twoSum(self,
               nums: List[int],    # list of integers
               target: int         # single integer
              ) -> List[int]:      # returns a list of two integers

        seen = {}                  # empty dict: will store {value: index}

        for i, num in enumerate(nums):    # i = index, num = value
            complement = target - num     # what number do we need?

            if complement in seen:        # have we seen the complement before?
                return [seen[complement], i]   # yes → return both indices

            seen[num] = i                 # no → store this number's index
```

### `anagram-groups` — Line by Line

```python
from collections import defaultdict    # import defaultdict from collections

class Solution:
    def groupAnagrams(self,
                      strs: List[str]       # list of strings
                     ) -> List[List[str]]:  # returns list of lists of strings

        anagram_map = defaultdict(list)  # dict where missing keys auto-create []
        return_list = []

        for s in strs:                        # s takes each word
            sorted_s = tuple(sorted(s))       # sort chars: "eat" → ('a','e','t')
            anagram_map[sorted_s].append(s)   # group by sorted key

        for v in anagram_map.values():        # v = each group (a list)
            return_list.append(v)

        return return_list

# Cleaner version of the last part:
        return list(anagram_map.values())     # same result, one line
```

---

## Summary Cheat Sheet

```python
# FUNCTION
def name(param1: type, param2: type) -> return_type:
    # body (indented)
    return value

# FOR LOOP FORMS
for item in collection:          # over any iterable
for i in range(n):               # 0 to n-1
for i in range(a, b):            # a to b-1
for i, val in enumerate(lst):    # index + value
for k, v in d.items():           # dict key + value

# WHILE LOOP
while condition:
    # body
    # must update condition to avoid infinite loop

# IF
if condition:
    ...
elif other_condition:
    ...
else:
    ...

# RETURN
return value          # return a value and exit
return                # exit with None
return a, b           # return two values (tuple)
```
