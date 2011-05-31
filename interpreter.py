import string
import sys
from unittest.case import TestCase
from tb import Tokenizer, Token

__author__ = 'Tony Edgecombe'


class Interpreter:
    def __init__(self):
        self.lines = {}
        self.variables = dict.fromkeys([x for x in string.ascii_uppercase], 0)

    def run(self):
        while True:
            line = input('>')
            self.interpret_line(line)


    def interpret_line(self, line):
        tokenizer = Tokenizer()
        tokenizer.parse(line)

        first_token = tokenizer.getNextToken()
        if first_token.type == Token.NUMBER:
            self.lines[int(first_token.value)] = tokenizer.prog[tokenizer.pos:]
            self.sort_lines()
        else:
            self.run_line(line)

    def run_line(self, line):
        tokenizer = Tokenizer()
        tokenizer.parse(line)

        statement = tokenizer.getNextToken()
        if statement.type != Token.COMMAND:
            raise Exception('Line not a statement')

        if statement.value == "LET":
            self.stat_let(tokenizer)
        elif statement.value == "PRINT":
            self.stat_print(tokenizer)
        elif statement.value == "LIST":
            self.stat_list(tokenizer)
        else:
            raise Exception('Unrecognised statement: ' + statement.value)

    def stat_let(self, tokenizer):
        variable = tokenizer.getNextToken()
        if variable.type != Token.VARIABLE:
            raise Exception("Expected a variable")

        if tokenizer.getNextToken().type != Token.EQUALS:
            raise Exception("Expected an equals")

        self.variables[variable.value] = self.match_expression(tokenizer)

    def match_expression_list(self, tokenizer):
        list = [self.match_expression(tokenizer)]

        while tokenizer.peekNextToken().type == Token.COMMA:
            tokenizer.getNextToken()
            list.append(self.match_expression(tokenizer))

        return list


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
            return factor.value
        elif factor.type == Token.VARIABLE:
            return self.variables[factor.value]
        else:
            raise Exception('Unexpected type for factor')

    def stat_print(self, tokenizer):
        list = self.match_expression_list(tokenizer)
        for v in list:
            print(v)

    def stat_list(self, tokenizer):
        for no, line in iter(self.lines.items()):
            print(no, line,)

    def sort_lines(self):
        s = sorted(self.lines.items(), key=lambda x: x[0])
        self.lines = dict(s)



class TestInterpreter(TestCase):
    def test_init(self):
        interpreter = Interpreter()
        self.assertEqual(26, len(interpreter.variables))
        self.assertEqual(0, interpreter.variables['A'])

    def test_set_line(self):
        interpreter = Interpreter()
        interpreter.interpret_line('10 LET A = 100')

        self.assertEqual(1, len(interpreter.lines))
        self.assertEqual({10:' LET A = 100'}, interpreter.lines)

        interpreter.interpret_line('20 PRINT A')
        self.assertEqual(2, len(interpreter.lines))
        self.assertEqual(' PRINT A', interpreter.lines[20])

    def test_let(self):
        interpreter = Interpreter()
        interpreter.run_line('LET B = 123 + 2')
        self.assertEqual(125, interpreter.variables['B'])

    def test_expression_list(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2+3+2*2, 1+2, 3')
        interpreter = Interpreter()

        self.assertEqual([9,3,3], interpreter.match_expression_list(tokenizer))


    def test_expression(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2+3+2*2')
        interpreter = Interpreter()

        self.assertEqual(9, interpreter.match_expression(tokenizer))

    def test_match_term(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2*3*4')
        interpreter = Interpreter()

        self.assertEqual(24, interpreter.match_term(tokenizer))

    def test_match_factor(self):
        tokenizer = Tokenizer()
        tokenizer.parse('123')
        interpreter = Interpreter()

        self.assertEqual(123, interpreter.match_factor(tokenizer))

        interpreter.variables['A'] = 456
        tokenizer.parse('A')
        self.assertEqual(456, interpreter.match_factor(tokenizer))




if __name__ == '__main__':
    print('Tiny Basic in Python')
    interp = Interpreter()
    interp.run()