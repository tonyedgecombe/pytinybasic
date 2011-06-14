from tokenizer import Token

class Parser:
    def __init__(self, variables):
        self._variables = variables

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
            return int(self._variables.get(factor.value, 0))
        elif factor.type == Token.LBRACKET:
            return self.match_bracketed_expression(tokenizer)
        else:
            raise Exception('Unexpected type for factor')

    def match_bracketed_expression(self, tokenizer):
        result = self.match_expression(tokenizer)

        if tokenizer.getNextToken().type != Token.RBRACKET:
            raise Exception('Expected closing bracket')

        return result


