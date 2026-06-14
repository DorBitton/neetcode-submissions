class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # First messy solution
        target = 0
        result = []
        nums = sorted(nums)

        for i in range(len(nums)):
            if (i > 0 and nums[i-1] == nums[i]):
                continue
            left = i + 1
            right = len(nums) - 1
            while (left < right):
                currentSum = nums[i] + nums[left] + nums[right]
                if (currentSum == target):
                    result.append([nums[i], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    left += 1
                    right -= 1
                elif currentSum < target:
                    left += 1
                else:
                    right -= 1

        return result