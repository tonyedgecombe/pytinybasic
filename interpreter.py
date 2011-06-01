from tbparser import Parser
from tokenizer import Tokenizer, Token

import string
from collections import OrderedDict
from unittest import TestCase

class Interpreter:
    def __init__(self):
        self.lines = {}

        self.program_counter = 0
        self.running = False

        self.stack = []

        self.variables = dict.fromkeys([x for x in string.ascii_uppercase], 0)
        self.parser = Parser(self.variables)

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
        statement = self.parser.match_statement(tokenizer)

        if statement == 'LET':
            self.stat_let(tokenizer)
        elif statement == 'PRINT':
            self.stat_print(tokenizer)
        elif statement == 'LIST':
            self.stat_list()
        elif statement == 'INPUT':
            self.stat_input(tokenizer)
        elif statement == 'IF':
            self.stat_if(tokenizer)
        elif statement == 'RUN':
            self.run_program()
        elif statement == 'END':
            self.stat_end()
        elif statement == 'GOTO':
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


    def stat_let(self, tokenizer):
        variable = tokenizer.getNextToken()
        if variable.type != Token.VARIABLE:
            raise Exception("Expected a variable")

        if tokenizer.getNextToken().type != Token.EQUALS:
            raise Exception('Expected an equals')

        self.parser.variables[variable.value] = self.parser.match_expression(tokenizer)


    def stat_print(self, tokenizer):
        list = self.parser.match_expression_list(tokenizer)
        print(','.join([str(i) for i in list]))

    def stat_list(self):
        for no, line in iter(self.lines.items()):
            print(no, line,)

    def stat_input(self, tokenizer):
        vars = self.parser.match_var_list(tokenizer)
        for var in vars:
            self.parser.variables[var] = input("?")

    def stat_if(self, tokenizer):
        result = self.parser.match_relop(tokenizer)

        then = tokenizer.getNextToken()
        if then.type != Token.COMMAND or then.value != 'THEN':
            raise Exception('Expected then after relative operator')

        if result:
            self.execute_statement(tokenizer)

    def stat_end(self):
        self.running = False

    def stat_goto(self, tokenizer):
        line_number = self.parser.match_expression(tokenizer)

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

    def test_init(self):
        self.assertEqual(26, len(self.interpreter.parser.variables))
        self.assertEqual(0, self.interpreter.parser.variables['A'])

    def test_set_line(self):
        self.interpreter.interpret_line('10 LET A = 100')

        self.assertEqual(1, len(self.interpreter.lines))
        self.assertEqual({10:' LET A = 100'}, self.interpreter.lines)

        self.interpreter.interpret_line('20 PRINT A')
        self.assertEqual(2, len(self.interpreter.lines))
        self.assertEqual(' PRINT A', self.interpreter.lines[20])

    def test_let(self):
        self.interpreter.run_line('LET B = 123 + 2')
        self.assertEqual(125, self.interpreter.parser.variables['B'])

    def test_if(self):
        self.interpreter.run_line('IF 2 < 1 THEN LET C = 100')
        self.assertEqual(0, self.interpreter.parser.variables['C'])

        self.interpreter.run_line('IF 2 > 1 THEN LET A = 100')
        self.assertEqual(100, self.interpreter.parser.variables['A'])

        self.interpreter.run_line('IF 1 THEN LET B = 200')
        self.assertEqual(200, self.interpreter.parser.variables['B'])

    def test_run_program(self):
        self.interpreter.lines[10] = 'LET A = 10'
        self.interpreter.lines[20] = 'LET B = 20'
        self.interpreter.lines[30] = 'LET C = A + B'
        self.interpreter.lines[40] = 'END'
        self.interpreter.lines[50] = 'LET C = 5'

        self.interpreter.run_program()

        self.assertEqual(30, self.interpreter.parser.variables['C'])

    def test_goto(self):
        self.interpreter.lines[10] = 'LET M = 1'
        self.interpreter.lines[20] = 'LET I = 0'

        self.interpreter.lines[30] = 'LET M = M * 2'
        self.interpreter.lines[40] = 'LET I = I + 1'
        self.interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'

        self.interpreter.run_program()

        self.assertEqual(256, self.interpreter.parser.variables['M'])

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

        self.assertEqual(256, self.interpreter.parser.variables['M'])

if __name__ == '__main__':
    print('Tiny Basic in Python')
    interp = Interpreter()
    interp.interactive()