from unittest import TestCase

from tokenizer import Token, Tokenizer

class Parser:
    def __init__(self, variables):
        self.variables = variables

    def match_statement(self, tokenizer):
        statement = tokenizer.getNextToken()
        if statement.type != Token.COMMAND:
            raise Exception('Line not a statement')

        return statement.value

    def match_relop(self, tokenizer):
        left = self.match_factor(tokenizer)

        relop = tokenizer.peekNextToken()
        if relop.type != Token.RELOP and relop.type != Token.EQUALS:
            return left

        tokenizer.getNextToken()
        right = self.match_factor(tokenizer)

        if relop.value == '<':
            return int(left < right)
        elif relop.value == '>':
            return int(left > right)
        elif relop.value == '<=':
            return int(left <= right)
        elif relop.value == '>=':
            return int(left >= right)
        elif relop.value == '=':
            return int(left == right)
        elif relop.value == '<>' or relop.value == '><':
            return int(left != right)
        else:
            raise Exception("Unimplemented relative operator: " + relop.value)

    def match_var_list(self, tokenizer):
        list = [self.match_var(tokenizer)]

        while tokenizer.peekNextToken().type == Token.COMMA:
            tokenizer.getNextToken()
            list.append(self.match_var(tokenizer))

        return list

    def match_var(self, tokenizer):
        token = tokenizer.getNextToken()
        if token.type != Token.VARIABLE:
            raise Exception("Expected a variable")

        return token.value

    def match_expression_list(self, tokenizer):
        if tokenizer.peekNextToken().type == Token.STRING:
            list = [self.match_string(tokenizer)]
        else:
            list = [self.match_expression(tokenizer)]

        while tokenizer.peekNextToken().type == Token.COMMA:
            tokenizer.getNextToken()

            if tokenizer.peekNextToken().type == Token.STRING:
                list.append(self.match_string(tokenizer))
            else:
                list.append(self.match_expression(tokenizer))

        return list

    def match_string(self, tokenizer):
        token = tokenizer.getNextToken()
        if token.type != Token.STRING:
            raise Exception("Not a string token")

        return token.value

    def match_expression(self, tokenizer):
        sign = 1
        token = tokenizer.peekNextToken()
        if token.type == Token.OPERATOR:
            tokenizer.getNextToken()
            if token.value == '-':
                sign = -1

        val = self.match_term(tokenizer)

        while tokenizer.peekNextToken().type == Token.OPERATOR:
            op = tokenizer.getNextToken()
            right = self.match_term(tokenizer)

            if op.value == '+':
                val = val + right
            else:
                val = val - right

        return sign * val

    def match_term(self, tokenizer):
        val = self.match_factor(tokenizer)

        while tokenizer.peekNextToken().type == Token.MULTOPERATOR:
            op = tokenizer.getNextToken()
            right = self.match_factor(tokenizer)

            if op.value == '*':
                val = val * right
            else:
                val = val / right

        return val

    def match_factor(self, tokenizer):
        factor = tokenizer.getNextToken()
        if factor.type == Token.NUMBER:
            return int(factor.value)
        elif factor.type == Token.VARIABLE:
            return int(self.variables.get(factor.value, 0))
        elif factor.type == Token.LBRACKET:
            return self.match_bracketed_expression(tokenizer)
        else:
            raise Exception('Unexpected type for factor')

    def match_bracketed_expression(self, tokenizer):
        result = self.match_expression(tokenizer)

        if tokenizer.getNextToken().type != Token.RBRACKET:
            raise Exception('Expected closing bracket')

        return result


class TestParser(TestCase):
    def setUp(self):
        self.tokenizer = Tokenizer()
        self.parser = Parser({})

    
    def test_match_var_list(self):
        self.tokenizer.parse('A, B, C')

        self.assertEqual(['A', 'B', 'C'], self.parser.match_var_list(self.tokenizer))


    def test_match_relop(self):
        self.tokenizer.parse('2 > 1')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 < 1')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 <= 2')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 <= 1')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 >= 2')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 >= 3')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 = 2')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 = 3')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 <> 3')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 <> 2')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 >< 3')
        self.assertEqual(1, self.parser.match_relop(self.tokenizer))

        self.tokenizer.parse('2 >< 2')
        self.assertEqual(0, self.parser.match_relop(self.tokenizer))


    def test_match_expression_list(self):
        self.tokenizer.parse('2+3+2*2, 1+2, 3, "abcd"')

        self.assertEqual([9,3,3, 'abcd'], self.parser.match_expression_list(self.tokenizer))

    def test_match_expression(self):
        self.tokenizer.parse('2+3+2*2')

        self.assertEqual(9, self.parser.match_expression(self.tokenizer))

    def test_match_term(self):
        self.tokenizer.parse('2*3*4')

        self.assertEqual(24, self.parser.match_term(self.tokenizer))

    def test_match_factor(self):
        self.tokenizer.parse('123')

        self.assertEqual(123, self.parser.match_factor(self.tokenizer))

        self.parser.variables['A'] = 456
        self.tokenizer.parse('A')
        self.assertEqual(456, self.parser.match_factor(self.tokenizer))

    def test_match_brackets(self):
        self.tokenizer.parse('(1 + 2) * (3 + 5)')
        self.assertEqual(24, self.parser.match_expression(self.tokenizer))