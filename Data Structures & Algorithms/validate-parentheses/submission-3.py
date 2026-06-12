class Solution:
    def isValid(self, s: str) -> bool:
        valid_check = {
            '}': '{',
            ']': '[',
            ')': '(' 
        }

        stack = []

        for char in s:
            if char in valid_check:
                if not stack:
                    return False
                top = stack.pop()
                if valid_check[char] != top:
                    return False
            else:
                stack.append(char)
        if not stack:
            return True
        else:
            return False