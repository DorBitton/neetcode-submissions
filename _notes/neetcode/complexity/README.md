# Time & Space Complexity

Understanding Big-O is essential — interviewers always ask about it.

## The Big-O Scale (fastest to slowest)

| Notation | Name | Example |
|---|---|---|
| O(1) | Constant | Dictionary lookup, array index access |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Single loop through array |
| O(n log n) | Log-linear | Merge sort, heap sort |
| O(n²) | Quadratic | Nested loops |
| O(2ⁿ) | Exponential | Recursive subsets |
| O(n!) | Factorial | All permutations |

## How to Analyze Code

1. **Count loops** — each nested loop multiplies the complexity
2. **Recursive calls** — draw a recursion tree and count nodes
3. **Built-in operations** — know the cost of Python built-ins:
   - `list.append()` → O(1) amortized
   - `list.insert(0, x)` → O(n)  ← common mistake!
   - `x in list` → O(n)
   - `x in set` → O(1)
   - `dict[key]` → O(1)
   - `sorted()` → O(n log n)

## Space Complexity

- Count the **extra** memory your algorithm uses (not the input itself)
- Recursion depth counts as stack space: O(depth)

---

> Add worked examples here as you encounter problems.
