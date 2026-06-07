from collections import defaultdict

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        frequency_map = defaultdict(int)
        for num in nums:
            frequency_map[num] += 1

        sorted_map = sorted(frequency_map.items(), key=lambda item: item[1] , reverse=True)

        sorted_map = sorted_map[:k]

        return_list = [item[0] for item in sorted_map]

        return return_list
