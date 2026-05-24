class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False
        
        cntS = Counter(s)
        cntT = Counter(t)

        return cntS == cntT