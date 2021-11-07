# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""

from token_ import Token, ClauseToken

class VALUE(Token):
    def _run(self, interpreter):
        value = self.TOKEN_FACTORY.create_value(self.value)
        interpreter.stack_append(value)

class INTEGER(VALUE):
    VALUE_FACTORY = int

class FLOAT(VALUE):
    VALUE_FACTORY = float

class TRUE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=1)

class FALSE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=0)

class VARNAME(VALUE):
    def _run(self, interpreter):
        if interpreter.check_variable(self.value):
            variable = interpreter.get_variable(self.value)
        else:
            variable = self.TOKEN_FACTORY.create_variable(self.value)

        interpreter.stack_append(variable)
        interpreter.set_variable('it', variable)

class ASSIGN_R(Token):
    pass

class ASSIGN_L(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME, ), (ASSIGN_R, ), (VALUE, )]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.value
        interpreter.set_variable(variable.name, variable)

class FROM(Token):
    pass

class TIMES(Token):
    pass

class BY(Token):
    pass

class AS(Token):
    pass

class PRINT(Token):

    RESOLUTION_ORDER = [1, 0]
    EXPECTED_TOKENS = [(Token, )]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        print(value.value)

class ADD(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE, ), (ASSIGN_R, ), (VARNAME, )]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value += value.value

class SUBTRACT(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE, ), (FROM, ), (VARNAME, )]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value -= value.value

class MULTIPLY(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME, ), (TIMES, ), (VALUE, )]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value *= value.value

class DIVIDE(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME, ), (BY, ), (VALUE, )]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value /= value.value
        if variable.value == int(variable.value):
            variable.value = int(variable.value)

class IT(VARNAME):
    def _run(self, interpreter):
        variable = interpreter.get_variable('it')
        interpreter.stack_append(variable)

class LINEBREAK(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)

    def update_token_factory(self, token_factory):
        token_factory.line_number += 1

class COMMENT(Token):
    def pop_tokens(self, tokens):
        popped_tokens = []
        while tokens:
            token = tokens.pop(0)
            popped_tokens.append(token)
            if isinstance(token, LINEBREAK):
                break
        return popped_tokens

class AND(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)

class END(Token):
    pass

class CLAUSE(ClauseToken):

    CLOSE_TOKEN = END

    def _run(self, interpreter):
        def run_tokens(interpreter):
            for token in self.tokens:
                token.run(interpreter)
        interpreter.stack_append(run_tokens)

class FUNCTION(Token):
    def _run(self, interpreter):
        function = interpreter.stack_pop()
        code = interpreter.stack_pop()
        interpreter.set_variable(function.name, code)

class DEFINE(Token):
    RESOLUTION_ORDER = [4, 3, 2, 1]
    EXPECTED_TOKENS = [(FUNCTION, ), (VARNAME, ), (AS, ), (CLAUSE, )]

class CALL(Token):
    RESOLUTION_ORDER = [1, 0]
    EXPECTED_TOKENS = [(VARNAME, )]

    def _run(self, interpreter):
        function = interpreter.stack_pop()
        function(interpreter)

tokens = {'set': ASSIGN_L,
          'to': ASSIGN_R,
          'from': FROM,
          'by': BY,
          'times': TIMES,
          'print': PRINT,
          'add': ADD,
          'subtract': SUBTRACT,
          'multiply': MULTIPLY,
          'divide': DIVIDE,
          'it': IT,
           'and': AND,
           'true': TRUE,
           'false': FALSE,
          '\n': LINEBREAK,
          '__tab__': CLAUSE,
          'define': DEFINE,
          'function': FUNCTION,
          'as': AS,
          'end': END,
          'call': CALL,
          }

regex_tokens = {r'^\d+$': INTEGER,
                r'^\w+$': VARNAME,
                r'^\d+\.\d+': FLOAT,
                r'^#.+?': COMMENT,
                }
