from collections import OrderedDict
import string
from unittest.case import TestCase
from tb import Tokenizer, Token

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
        statement = tokenizer.getNextToken()
        if statement.type != Token.COMMAND:
            raise Exception('Line not a statement')

        if statement.value == "LET":
            self.stat_let(tokenizer)
        elif statement.value == "PRINT":
            self.stat_print(tokenizer)
        elif statement.value == "LIST":
            self.stat_list()
        elif statement.value == "INPUT":
            self.stat_input(tokenizer)
        elif statement.value == "IF":
            self.stat_if(tokenizer)
        elif statement.value == "RUN":
            self.run_program()
        elif statement.value == "END":
            self.stat_end()
        elif statement.value == "GOTO":
            self.stat_goto(tokenizer)
        elif statement.value == 'GOSUB':
            self.stat_gosub(tokenizer)
        elif statement.value == 'RETURN':
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

    def test_if(self):
        interpreter = Interpreter()

        interpreter.run_line('IF 2 < 1 THEN LET C = 100')
        self.assertEqual(0, interpreter.variables['C'])

        interpreter.run_line('IF 2 > 1 THEN LET A = 100')
        self.assertEqual(100, interpreter.variables['A'])

        interpreter.run_line('IF 1 THEN LET B = 200')
        self.assertEqual(200, interpreter.variables['B'])

    def test_match_var_list(self):
        tokenizer = Tokenizer()
        tokenizer.parse('A, B, C')
        interpreter = Interpreter()

        self.assertEqual(['A', 'B', 'C'], interpreter.match_var_list(tokenizer))


    def test_match_relop(self):
        tokenizer = Tokenizer()
        interpreter = Interpreter()

        tokenizer.parse("2 > 1")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 < 1")
        self.assertEqual(0, interpreter.match_relop(tokenizer))
        
        tokenizer.parse("2 <= 2")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 <= 1")
        self.assertEqual(0, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 >= 2")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 >= 3")
        self.assertEqual(0, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 = 2")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 = 3")
        self.assertEqual(0, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 <> 3")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 <> 2")
        self.assertEqual(0, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 >< 3")
        self.assertEqual(1, interpreter.match_relop(tokenizer))

        tokenizer.parse("2 >< 2")
        self.assertEqual(0, interpreter.match_relop(tokenizer))


    def test_expression_list(self):
        tokenizer = Tokenizer()
        tokenizer.parse('2+3+2*2, 1+2, 3, "abcd"')
        interpreter = Interpreter()

        self.assertEqual([9,3,3, 'abcd'], interpreter.match_expression_list(tokenizer))


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


    def test_run_program(self):
        interpreter = Interpreter()

        interpreter.lines[10] = 'LET A = 10'
        interpreter.lines[20] = 'LET B = 20'
        interpreter.lines[30] = 'LET C = A + B'
        interpreter.lines[40] = 'END'
        interpreter.lines[50] = 'LET C = 5'

        interpreter.run_program()

        self.assertEqual(30, interpreter.variables['C'])

    def test_goto(self):
        interpreter = Interpreter()

        interpreter.lines[10] = 'LET M = 1'
        interpreter.lines[20] = 'LET I = 0'

        interpreter.lines[30] = 'LET M = M * 2'
        interpreter.lines[40] = 'LET I = I + 1'
        interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'

        interpreter.run_program()

        self.assertEqual(256, interpreter.variables['M'])

    def test_gosub(self):
        interpreter = Interpreter()

        interpreter.lines[10] = 'LET M = 1'
        interpreter.lines[20] = 'LET I = 0'

        interpreter.lines[30] = 'GOSUB 70'
        interpreter.lines[40] = 'LET I = I + 1'
        interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'
        interpreter.lines[60] = 'END'
        interpreter.lines[70] = 'LET M = M * 2'
        interpreter.lines[80] = 'RETURN'

        interpreter.run_program()

        self.assertEqual(256, interpreter.variables['M'])

if __name__ == '__main__':
    print('Tiny Basic in Python')
    interp = Interpreter()
    interp.interactive()