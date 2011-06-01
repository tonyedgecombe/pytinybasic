import string
from collections import OrderedDict
from unittest.case import TestCase
from tokenizer import Tokenizer, Token

__author__ = 'Tony Edgecombe'

class Interpreter:
    def __init__(self):
        self.lines = {}
        self.variables = dict.fromkeys([x for x in string.ascii_uppercase], 0)

        self.program_counter = 0
        self.running = False

        self.stack = []

    def interactive(self):
        while True:
            line = input('>')
            if len(line):
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
        self.execute_statement(tokenizer)
        
    def execute_statement(self, tokenizer):
        statement = self.match_statement(tokenizer)

        if statement == "LET":
            self.stat_let(tokenizer)
        elif statement == "PRINT":
            self.stat_print(tokenizer)
        elif statement == "LIST":
            self.stat_list()
        elif statement == "INPUT":
            self.stat_input(tokenizer)
        elif statement == "IF":
            self.stat_if(tokenizer)
        elif statement == "RUN":
            self.run_program()
        elif statement == "END":
            self.stat_end()
        elif statement == "GOTO":
            self.stat_goto(tokenizer)
        elif statement == 'GOSUB':
            self.stat_gosub(tokenizer)
        elif statement == 'RETURN':
            self.stat_return()
        else:
            raise Exception('Unrecognised statement: ' + statement.value)

    def run_program(self):
        self.program_counter = 0
        self.running = True

        self.sort_lines()

        statements = [x for x in self.lines.values()]

        while self.program_counter < len(statements) and self.running:
            statement = statements[self.program_counter]

            self.run_line(statement)
            self.program_counter += 1
        
    def sort_lines(self):
        self.lines = OrderedDict(sorted(self.lines.items(), key=lambda x: x[0]))

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
            return int(self.variables[factor.value])
        else:
            raise Exception('Unexpected type for factor')


    def stat_let(self, tokenizer):
        variable = tokenizer.getNextToken()
        if variable.type != Token.VARIABLE:
            raise Exception("Expected a variable")

        if tokenizer.getNextToken().type != Token.EQUALS:
            raise Exception("Expected an equals")

        self.variables[variable.value] = self.match_expression(tokenizer)


    def stat_print(self, tokenizer):
        list = self.match_expression_list(tokenizer)
        print(','.join([str(i) for i in list]))

    def stat_list(self):
        for no, line in iter(self.lines.items()):
            print(no, line,)

    def stat_input(self, tokenizer):
        vars = self.match_var_list(tokenizer)
        for var in vars:
            self.variables[var] = input("?")

    def stat_if(self, tokenizer):
        result = self.match_relop(tokenizer)

        then = tokenizer.getNextToken()
        if then.type != Token.COMMAND or then.value != "THEN":
            raise Exception("Expected then after relative operator")

        if result:
            self.execute_statement(tokenizer)

    def stat_end(self):
        self.running = False

    def stat_goto(self, tokenizer):
        line_number = self.match_expression(tokenizer)

        self.sort_lines()
        line_numbers = [x for x in self.lines.keys()]
        self.program_counter = line_numbers.index(line_number) - 1

    def stat_gosub(self, tokenizer):
        self.stack.append(self.program_counter)
        self.stat_goto(tokenizer)

    def stat_return(self):
        self.program_counter = self.stack.pop()


class TestInterpreter(TestCase):
    def setUp(self):
        self.interpreter = Interpreter()
        self.tokenizer = Tokenizer()

    def test_init(self):
        self.assertEqual(26, len(self.interpreter.variables))
        self.assertEqual(0, self.interpreter.variables['A'])

    def test_set_line(self):
        self.interpreter.interpret_line('10 LET A = 100')

        self.assertEqual(1, len(self.interpreter.lines))
        self.assertEqual({10:' LET A = 100'}, self.interpreter.lines)

        self.interpreter.interpret_line('20 PRINT A')
        self.assertEqual(2, len(self.interpreter.lines))
        self.assertEqual(' PRINT A', self.interpreter.lines[20])

    def test_let(self):
        self.interpreter.run_line('LET B = 123 + 2')
        self.assertEqual(125, self.interpreter.variables['B'])

    def test_if(self):
        self.interpreter.run_line('IF 2 < 1 THEN LET C = 100')
        self.assertEqual(0, self.interpreter.variables['C'])

        self.interpreter.run_line('IF 2 > 1 THEN LET A = 100')
        self.assertEqual(100, self.interpreter.variables['A'])

        self.interpreter.run_line('IF 1 THEN LET B = 200')
        self.assertEqual(200, self.interpreter.variables['B'])

    def test_match_var_list(self):
        self.tokenizer.parse('A, B, C')

        self.assertEqual(['A', 'B', 'C'], self.interpreter.match_var_list(self.tokenizer))


    def test_match_relop(self):
        self.tokenizer.parse("2 > 1")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 < 1")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))
        
        self.tokenizer.parse("2 <= 2")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 <= 1")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 >= 2")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 >= 3")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 = 2")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 = 3")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 <> 3")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 <> 2")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 >< 3")
        self.assertEqual(1, self.interpreter.match_relop(self.tokenizer))

        self.tokenizer.parse("2 >< 2")
        self.assertEqual(0, self.interpreter.match_relop(self.tokenizer))


    def test_expression_list(self):
        self.tokenizer.parse('2+3+2*2, 1+2, 3, "abcd"')

        self.assertEqual([9,3,3, 'abcd'], self.interpreter.match_expression_list(self.tokenizer))


    def test_expression(self):
        self.tokenizer.parse('2+3+2*2')

        self.assertEqual(9, self.interpreter.match_expression(self.tokenizer))

    def test_match_term(self):
        self.tokenizer.parse('2*3*4')

        self.assertEqual(24, self.interpreter.match_term(self.tokenizer))

    def test_match_factor(self):
        self.tokenizer.parse('123')

        self.assertEqual(123, self.interpreter.match_factor(self.tokenizer))

        self.interpreter.variables['A'] = 456
        self.tokenizer.parse('A')
        self.assertEqual(456, self.interpreter.match_factor(self.tokenizer))


    def test_run_program(self):
        self.interpreter.lines[10] = 'LET A = 10'
        self.interpreter.lines[20] = 'LET B = 20'
        self.interpreter.lines[30] = 'LET C = A + B'
        self.interpreter.lines[40] = 'END'
        self.interpreter.lines[50] = 'LET C = 5'

        self.interpreter.run_program()

        self.assertEqual(30, self.interpreter.variables['C'])

    def test_goto(self):
        self.interpreter.lines[10] = 'LET M = 1'
        self.interpreter.lines[20] = 'LET I = 0'

        self.interpreter.lines[30] = 'LET M = M * 2'
        self.interpreter.lines[40] = 'LET I = I + 1'
        self.interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'

        self.interpreter.run_program()

        self.assertEqual(256, self.interpreter.variables['M'])

    def test_gosub(self):
        self.interpreter.lines[10] = 'LET M = 1'
        self.interpreter.lines[20] = 'LET I = 0'

        self.interpreter.lines[30] = 'GOSUB 70'
        self.interpreter.lines[40] = 'LET I = I + 1'
        self.interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'
        self.interpreter.lines[60] = 'END'
        self.interpreter.lines[70] = 'LET M = M * 2'
        self.interpreter.lines[80] = 'RETURN'

        self.interpreter.run_program()

        self.assertEqual(256, self.interpreter.variables['M'])

if __name__ == '__main__':
    print('Tiny Basic in Python')
    interp = Interpreter()
    interp.interactive()