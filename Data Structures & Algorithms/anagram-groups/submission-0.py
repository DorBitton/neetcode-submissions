class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        d = {}

        for s in strs:
            key = "".join(sorted(s))
            if key not in d:
                d[key] = []
            d[key].append(s)
            print(key)
        return list(d.values()) 