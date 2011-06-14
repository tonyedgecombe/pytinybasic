from unittest import TestCase
from tokenizer import Tokenizer, Token

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
        self.assertEqual('A', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.OPERATOR, token.type)
        self.assertEqual('+', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.STRING, token.type)
        self.assertEqual('B', token.value)

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
        self.assertEqual('PRINT', token.value)

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
        self.assertEqual('LET', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.VARIABLE, token.type)
        self.assertEqual('A', token.value)

        token = self.tokenizer.getNextToken()
        self.assertEqual(token.EQUALS, token.type)
        self.assertEqual('=', token.value)

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


    def test_brackets(self):
        self.tokenizer.parse('(100)')

        token = self.tokenizer.getNextToken()
        self.assertEqual(Token.LBRACKET, token.type)
        self.assertEqual('(', token.value)

        self.assertEqual(Token.NUMBER, self.tokenizer.getNextToken().type)

        token = self.tokenizer.getNextToken()
        self.assertEqual(Token.RBRACKET, token.type)
        self.assertEqual(')', token.value)

