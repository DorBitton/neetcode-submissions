class Solution:
    def maxArea(self, heights: List[int]) -> int:
            left, right = 0, len(heights) - 1
            maxArea = 0
            while (left < right):
                if (heights[left] > heights[right]):
                    currentArea = (right - left ) * heights[right]
                elif (heights[left] < heights[right]):
                    currentArea = (right - left ) * heights[left]
                else:
                    currentArea = (right - left ) * heights[right]

                if (currentArea >  maxArea):
                    maxArea = currentArea

                if (heights[left] > heights[right]):
                    right -= 1
                elif (heights[left] < heights[right]):
                    left += 1
                else:
                    right -= 1

            return maxArea
