from collections import defaultdict
from typing import List

class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:        
        anagram_map = defaultdict(list)

        for word in strs:
            sorted_key = "".join(sorted(word))
            anagram_map[sorted_key].append(word)
        return list(anagram_map.values())