__author__ = 'Tony Edgecombe'

from unittest.case import TestCase


class Token:
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2
    OPERATOR = 3
    MULTOPERATOR = 4
    COMMAND = 5

    type = UNKNOWN
    value = None



class Tokenizer:
    def parse(self, prog):
        self.prog = prog
        self.pos = 0

    def getNextToken(self):
        if self.currentChar().isdigit():
            return self.getNumberToken()
        elif self.currentChar() == '"':
            return self.getStringToken()
        elif self.currentChar() == '+' or self.currentChar() == '-':
            return self.getOperator()
        elif self.currentChar() == '*' or self.currentChar() == '/':
            return self.getMultOperator()


        token = Token()
        return token

    def getNumberToken(self):
        token = Token()
        token.type = token.NUMBER
        token.value = 0

        while self.pos < len(self.prog) and self.currentChar().isdigit():
            token.value = token.value * 10 + int(self.currentChar())
            self.pos += 1

        return token

    def getStringToken(self):
        token = Token()
        token.type = token.STRING
        token.value = ''

        while self.pos < len(self.prog):
            self.pos += 1

            if self.currentChar() == '"':
                self.pos += 1
                return token

            token.value = token.value + self.currentChar()

        raise Exception('String not terminated')

    def getOperator(self):
        token = Token()
        token.type = token.OPERATOR
        token.value = self.currentChar()

        self.pos += 1

        return token

    def getMultOperator(self):
        token = Token()
        token.type = token.MULTOPERATOR
        token.value = self.currentChar()

        self.pos += 1

        return token

    def currentChar(self):
        return self.prog[self.pos]

    def nextChar(self):
        return self.prog[self.pos + 1]


class TestTokeniser(TestCase):
    def test_number(self):
        tokenizer = Tokenizer()
        tokenizer.parse('100')
        token = tokenizer.getNextToken()

        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(100, token.value)

    def test_string(self):
        tokenizer = Tokenizer()
        tokenizer.parse('"ABC"')
        token = tokenizer.getNextToken()

        self.assertEqual(token.STRING, token.type)
        self.assertEqual('ABC', token.value)

    def test_operator(self):
        tokenizer = Tokenizer()
        tokenizer.parse('1+2-4')

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(1, token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('-', token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(4, token.value)

    def test_operator2(self):
        tokenizer = Tokenizer()
        tokenizer.parse('"A"+"B"')

        token = tokenizer.getNextToken()
        self.assertEqual(token.STRING, token.type)
        self.assertEqual("A", token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.STRING, token.type)
        self.assertEqual("B", token.value)

    def test_mult_operator(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2*3')

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.MULTOPERATOR, token.type)
        self.assertEqual('*', token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(3, token.value)


    def test_mult_operator2(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2/3')

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.MULTOPERATOR, token.type)
        self.assertEqual('/', token.value)

        token = tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(3, token.value)



