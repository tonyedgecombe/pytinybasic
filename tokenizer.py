from unittest import TestCase

class Token:
    UNKNOWN = 0
    NUMBER = 1
    STRING = 2
    OPERATOR = 3
    MULTOPERATOR = 4
    COMMAND = 5
    VARIABLE = 6
    RELOP = 7
    EOF = 8
    EQUALS = 9
    COMMA = 10
        
    def __init__(self, type = UNKNOWN, value = None):
        self.type = type
        self.value = value


class Tokenizer:
    def parse(self, prog):
        self.prog = prog
        self.pos = 0

    def currentChar(self):
        return self.prog[self.pos]

    def nextChar(self):
        if self.pos + 1 < len(self.prog):
            return self.prog[self.pos + 1]
        else:
            return None

    def eatWhiteSpace(self):
        while self.pos < len(self.prog) and self.currentChar().isspace():
            self.pos += 1

    def getNextToken(self):
        self.eatWhiteSpace()

        if self.pos >= len(self.prog):
            return Token(Token.EOF)

        c = self.currentChar()

        if c.isdigit():
            return self.getNumberToken()
        elif c == '"':
            return self.getStringToken()
        elif c == '+' or c == '-':
            return self.getOperator()
        elif c == '*' or c == '/':
            return self.getMultOperator()
        elif c.isalpha() and self.nextChar() != None and self.nextChar().isalpha():
            return self.getCommand()
        elif c.isalpha():
            return self.getVariable()
        elif c == '<' or c == '>':
            return self.getRelativeOperator()
        elif c == '=':
            return self.getEquals()
        elif c == ',':
            return self.getComma()

        return Token()

    def peekNextToken(self):
        pos = self.pos
        token = self.getNextToken()
        self.pos = pos

        return token

    def getNumberToken(self):
        token = Token(Token.NUMBER, 0)

        while self.pos < len(self.prog) and self.currentChar().isdigit():
            token.value = token.value * 10 + int(self.currentChar())
            self.pos += 1

        return token

    def getStringToken(self):
        token = Token(Token.STRING, '')

        while self.pos < len(self.prog):
            self.pos += 1

            if self.currentChar() == '"':
                self.pos += 1
                return token

            token.value = token.value + self.currentChar()

        raise Exception('String not terminated')

    def getOperator(self):
        token = Token(Token.OPERATOR, self.currentChar())
        self.pos += 1

        return token

    def getMultOperator(self):
        token = Token(Token.MULTOPERATOR, self.currentChar())
        self.pos += 1

        return token

    def getCommand(self):
        token = Token(Token.COMMAND, '')

        while self.pos < len(self.prog) and self.currentChar().isalpha():
            token.value += self.currentChar()
            self.pos += 1        

        return token

    def getVariable(self):
        token = Token(Token.VARIABLE, self.currentChar())
        self.pos += 1

        return token

    def getRelativeOperator(self):
        token = Token(Token.RELOP, self.currentChar())

        if self.pos + 1 < len(self.prog) and (self.nextChar() == '=' or self.nextChar() == '>' or self.nextChar() == '<'):
            token.value += self.nextChar()
            self.pos += 1

        self.pos += 1
        
        return token

    def getEquals(self):
        token = Token(Token.EQUALS, '=')
        self.pos += 1

        return token

    def getComma(self):
        token = Token(Token.COMMA, ',')
        self.pos += 1

        return token



class TestTokeniser(TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()

    def test_number(self):
        self.tokenizer.parse('100')
        token = self.tokenizer.getNextToken()

        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(100, token.value)

    def test_string(self):
        self.tokenizer.parse('"ABC"')
        token = self.tokenizer.getNextToken()

        self.assertEqual(token.STRING, token.type)
        self.assertEqual('ABC', token.value)

    def test_peek_token(self):
        self.tokenizer.parse('1+2')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(1, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = self.tokenizer.peekNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)


    def test_operator(self):
        self.tokenizer.parse('1+2-4')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(1, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('-', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(4, token.value)

    def test_operator2(self):
        self.tokenizer.parse('"A"+"B"')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.STRING, token.type)
        self.assertEqual("A", token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.STRING, token.type)
        self.assertEqual("B", token.value)

    def test_mult_operator(self):
        self.tokenizer.parse('2*3')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.MULTOPERATOR, token.type)
        self.assertEqual('*', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(3, token.value)


    def test_mult_operator2(self):
        self.tokenizer.parse('2/3')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(2, token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.MULTOPERATOR, token.type)
        self.assertEqual('/', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(3, token.value)


    def test_command(self):
        self.tokenizer.parse('PRINT 100')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.COMMAND, token.type)
        self.assertEqual("PRINT", token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(100, token.value)

    def test_variable(self):
        self.tokenizer.parse('D')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.VARIABLE, token.type)
        self.assertEqual('D', token.value)

    def test_relop_lessthan(self):
        self.tokenizer.parse('<')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('<', token.value)

    def test_relop_lessthanorequals(self):
        self.tokenizer.parse('<=')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('<=', token.value)

    def test_relop_notequals(self):
        self.tokenizer.parse('<>')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('<>', token.value)

    def test_relop_greater(self):
        self.tokenizer.parse('>')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('>', token.value)

    def test_relop_greateroreqials(self):
        self.tokenizer.parse('>=')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('>=', token.value)

    def test_relop_notequals2(self):
        self.tokenizer.parse('><')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.RELOP, token.type)
        self.assertEqual('><', token.value)


    def test_eof(self):
        self.tokenizer.parse('')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.EOF, token.type)

    def test_equals(self):
        self.tokenizer.parse('LET A = 100')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.COMMAND, token.type)
        self.assertEqual("LET", token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.VARIABLE, token.type)
        self.assertEqual("A", token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.EQUALS, token.type)
        self.assertEqual("=", token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.NUMBER, token.type)
        self.assertEqual(100, token.value)

    def test_comma(self):
        self.tokenizer.parse('A,B')

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.VARIABLE, token.type)
        self.assertEqual('A', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.COMMA, token.type)
        self.assertEqual(',', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.VARIABLE, token.type)
        self.assertEqual('B', token.value)

