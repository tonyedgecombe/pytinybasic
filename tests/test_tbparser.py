from unittest import TestCase
from tbparser import Parser
from tokenizer import Tokenizer

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

        self.parser._variables['A'] = 456
        self.tokenizer.parse('A')
        self.assertEqual(456, self.parser.match_factor(self.tokenizer))

    def test_match_brackets(self):
        self.tokenizer.parse('(1 + 2) * (3 + 5)')
        self.assertEqual(24, self.parser.match_expression(self.tokenizer))
