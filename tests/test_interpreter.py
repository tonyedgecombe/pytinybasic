from unittest import TestCase
from interpreter import Interpreter


class TestInterpreter(TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def test_init(self):
        self.assertEqual(0, self.interpreter._parser._variables.get('A', 0))

    def test_set_line(self):
        self.interpreter.interpret_line('10 LET A = 100')

        self.assertEqual(1, len(self.interpreter.lines))
        self.assertEqual({10:' LET A = 100'}, self.interpreter.lines)

        self.interpreter.interpret_line('20 PRINT A')
        self.assertEqual(2, len(self.interpreter.lines))
        self.assertEqual(' PRINT A', self.interpreter.lines[20])

    def test_let(self):
        self.interpreter.run_line('LET B = 123 + 2')
        self.assertEqual(125, self.interpreter._parser._variables['B'])

    def test_if(self):
        self.interpreter.run_line('IF 2 < 1 THEN LET C = 100')
        self.assertEqual(0, self.interpreter._parser._variables.get('C', 0))

        self.interpreter.run_line('IF 2 > 1 THEN LET A = 100')
        self.assertEqual(100, self.interpreter._parser._variables['A'])

        self.interpreter.run_line('IF 1 THEN LET B = 200')
        self.assertEqual(200, self.interpreter._parser._variables['B'])

    def test_run_program(self):
        self.interpreter.lines[10] = 'LET A = 10'
        self.interpreter.lines[20] = 'LET B = 20'
        self.interpreter.lines[30] = 'LET C = A + B'
        self.interpreter.lines[40] = 'END'
        self.interpreter.lines[50] = 'LET C = 5'

        self.interpreter.run_program()

        self.assertEqual(30, self.interpreter._parser._variables['C'])

    def test_goto(self):
        self.interpreter.lines[10] = 'LET M = 1'
        self.interpreter.lines[20] = 'LET I = 0'

        self.interpreter.lines[30] = 'LET M = M * 2'
        self.interpreter.lines[40] = 'LET I = I + 1'
        self.interpreter.lines[50] = 'IF I < 8 THEN GOTO 30'

        self.interpreter.run_program()

        self.assertEqual(256, self.interpreter._parser._variables['M'])

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

        self.assertEqual(256, self.interpreter._parser._variables['M'])
