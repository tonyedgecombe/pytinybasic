

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
    LBRACKET = 11
    RBRACKET = 12
        
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
        elif c == '(':
            return self.getLeftBracket()
        elif c == ')':
            return self.getRightBracket()

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

    def getLeftBracket(self):
        token = Token(Token.LBRACKET, '(')
        self.pos += 1

        return token

    def getRightBracket(self):
        token = Token(Token.RBRACKET, ')')
        self.pos += 1

        return token


