class Solution:

    def encode(self, strs: List[str]) -> str:
        result = []
        for word in strs:
            temp_word = str(len(word)) + '#' + word
            result.append(temp_word)

        return "".join(result)

    def decode(self, s: str) -> List[str]:
        decoded_strs = []
        i = 0
        while i < len(s):
            j = i
            while s[j] != '#':
                j += 1
            length = int(s[i:j])
            word = s[j + 1: j + 1 + length]
            decoded_strs.append(word)
            i = j + 1 + length
        return decoded_strs
