from tbparser import Parser
from tokenizer import Tokenizer, Token

from collections import OrderedDict

class Interpreter:
    def __init__(self):
        self.lines = {}

        self._program_counter = 0
        self._running = False

        self._stack = []

        self._variables = {}
        self._parser = Parser(self._variables)


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
        statement = self._parser.match_statement(tokenizer)

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
        self._program_counter = 0
        self._running = True

        self.sort_lines()

        statements = [x for x in self.lines.values()]

        while self._program_counter < len(statements) and self._running:
            statement = statements[self._program_counter]

            self.run_line(statement)
            self._program_counter += 1
        
    def sort_lines(self):
        self.lines = OrderedDict(sorted(self.lines.items(), key=lambda x: x[0]))


    def stat_let(self, tokenizer):
        variable = tokenizer.getNextToken()
        if variable.type != Token.VARIABLE:
            raise Exception("Expected a variable")

        if tokenizer.getNextToken().type != Token.EQUALS:
            raise Exception('Expected an equals')

        self._parser._variables[variable.value] = self._parser.match_expression(tokenizer)


    def stat_print(self, tokenizer):
        list = self._parser.match_expression_list(tokenizer)
        print(','.join([str(i) for i in list]))

    def stat_list(self):
        for no, line in iter(self.lines.items()):
            print(no, line,)

    def stat_input(self, tokenizer):
        vars = self._parser.match_var_list(tokenizer)
        for var in vars:
            self._parser._variables[var] = input("?")

    def stat_if(self, tokenizer):
        result = self._parser.match_relop(tokenizer)

        then = tokenizer.getNextToken()
        if then.type != Token.COMMAND or then.value != 'THEN':
            raise Exception('Expected then after relative operator')

        if result:
            self.execute_statement(tokenizer)

    def stat_end(self):
        self._running = False

    def stat_goto(self, tokenizer):
        line_number = self._parser.match_expression(tokenizer)

        self.sort_lines()
        line_numbers = [x for x in self.lines.keys()]
        self._program_counter = line_numbers.index(line_number) - 1

    def stat_gosub(self, tokenizer):
        self._stack.append(self._program_counter)
        self.stat_goto(tokenizer)

    def stat_return(self):
        self._program_counter = self._stack.pop()



if __name__ == '__main__':
    print('Tiny Basic in Python')
    interp = Interpreter()
    interp.interactive()