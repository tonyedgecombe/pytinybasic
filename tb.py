__author__ = 'Tony Edgecombe'

from unittest.case import TestCase


class Token:
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2

    type = UNKNOWN
    value = None



class Tokenizer:
    def parse(self, prog):
        self.prog = prog
        self.pos = 0

    def isDigit(self, chr):
        return chr >= '0' and chr <= '9'

    def getNextToken(self):
        if self.isDigit(self.prog[self.pos]):
            return self.getNumberToken()

        token = Token()
        return token

    def getNumberToken(self):
        token = Token()
        token.type = token.NUMBER
        token.value = 0

        while self.pos < len(self.prog) and self.isDigit(self.prog[self.pos]):
            token.value = token.value * 10 + int(self.prog[self.pos])
            self.pos = self.pos + 1

        return token


class TestTokeniser(TestCase):
    def test_number(self):
        tokenizer = Tokenizer()
        tokenizer.parse('100')
        token = tokenizer.getNextToken()

        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(100, token.value)

