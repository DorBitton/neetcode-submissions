class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        max_profit = 0
        smallest = 0

        for i in range(len(prices)):
            if i == 0:
                smallest = prices[i]

            if smallest > prices[i]:
                smallest = prices[i]

            if prices[i] > smallest:
                current_profit = prices[i] - smallest
                if (current_profit > max_profit):
                    max_profit = prices[i] - smallest

        return max_profit