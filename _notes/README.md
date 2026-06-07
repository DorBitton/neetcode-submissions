# My Interview Prep Notes

## Start Here When Solving a Problem

> **Open [`QUICK-REFERENCE.md`](./QUICK-REFERENCE.md) first.**
> It has all syntax, data structures, operations, and complexities on one page.

---

## File Map

### Reference Files (open while solving)

| File | What's in it |
|---|---|
| [`QUICK-REFERENCE.md`](./QUICK-REFERENCE.md) | Loops, strings, lists, set, dict, defaultdict, Counter, tuple, built-ins, Big-O |

### Deep-Dive Notes (read to understand, not during solving)

| File | What's in it |
|---|---|
| [`python-basics/python-syntax-and-loops.md`](./python-basics/python-syntax-and-loops.md) | Variables, functions, for/while loops, if/else, type hints, `self`, class syntax |
| [`python-basics/lists-and-nested-lists.md`](./python-basics/lists-and-nested-lists.md) | Lists, slicing, list of lists, 2D grids, `groupAnagrams` decoded line by line |
| [`data-structures/sets-and-hashmaps.md`](./data-structures/sets-and-hashmaps.md) | How hashing works, set internals, why `in` is O(1), dict, defaultdict, Counter |
| [`complexity/README.md`](./complexity/README.md) | Big-O scale, how to count loops, Python built-in costs |

### Progress & Planning

| File | What's in it |
|---|---|
| [`my-progress/progress-analysis.md`](./my-progress/progress-analysis.md) | Problems solved, patterns learned, what's next |

### To Fill In (as you learn)

| Folder | Status |
|---|---|
| `data-structures/` | List ✓, Set ✓, Dict ✓ — Stack, Queue, Tree, Heap TBD |
| `algorithms/` | Empty — fill as you reach each topic |
| `patterns/` | Empty — fill as you reach each pattern |

---

## How to Use These Notes

### When solving a new problem:
1. Open `QUICK-REFERENCE.md`
2. Identify what data structure the problem needs (see the "When to use which" table at the bottom)
3. Look up the syntax you need

### When you don't understand something in a solution:
1. Check the deep-dive note for that topic
2. If it's not there, ask and we'll add it

### After solving a problem:
1. Update your checklist in `my-progress/progress-analysis.md`

---

## What Each Note Covers vs Your Solutions

| Your Solution | Concepts Used | Where in Notes |
|---|---|---|
| `duplicate-integer` | set, `x in set` | QUICK-REFERENCE → Set; deep: sets-and-hashmaps.md |
| `is-anagram` | Counter, dict comparison | QUICK-REFERENCE → Counter; deep: sets-and-hashmaps.md |
| `two-integer-sum` | dict, enumerate, complement | QUICK-REFERENCE → Dict; deep: sets-and-hashmaps.md |
| `anagram-groups` | defaultdict, sorted, join, tuple | QUICK-REFERENCE → all sections; deep: lists-and-nested-lists.md |
