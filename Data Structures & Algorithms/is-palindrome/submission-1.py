class Solution:
    def isPalindrome(self, s: str) -> bool:
        ## Pyuthon slicing solution 
        s = [c.lower() for c in s if c.isalnum()]
        return s == s[::-1]