class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []

        for i in range(len(tokens)):
            if tokens[i] in ("+", "-", "*", "/"):
                num2 = int(stack.pop())
                num1 = int(stack.pop())

                if tokens[i] == "+":
                    calc = num1 + num2
                elif tokens[i] == "-":
                    calc = num1 - num2
                elif tokens[i] == "*":
                    calc = num1 * num2
                elif tokens[i] == "/":
                    # Use int() to truncate toward zero as required by the problem
                    calc = int(num1 / num2)

                stack.append(calc)
            else:
                stack.append(tokens[i])
        return int(stack[0])