class Solution:
    def maxArea(self, heights: List[int]) -> int:
            left, right = 0, (len(heights) - 1)
            maxArea = 0

            while (left < right):
                width = right - left
                height = min(heights[left], heights[right])
                currentArea = width * height

                if (currentArea > maxArea):
                    maxArea = currentArea

                if (heights[left] < heights[right]):
                    left += 1
                else:
                    right -= 1

            return maxArea
