class Solution:
    def isPalindrome(self, s: str) -> bool:
        # Two pointers solution:
        s = [c.lower() for c in s if c.isalnum()]
        left, right = 0, len(s)-1

        while (left<right):
            print(s[left])
            print(s[right])
            if s[left] == s[right]:
                left += 1
                right -= 1
            else:
                return False
        
        return True