# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""

from token_ import Token, ANYTYPE

class VALUE(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

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
    EXPECTED_TOKENS = [(VALUE)]

class ASSIGN_L(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (ASSIGN_R), (VALUE)]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.value
        interpreter.set_variable(variable.name, variable)

class FROM(Token):
    EXPECTED_TOKENS = [(VALUE)]

class TIMES(Token):
    EXPECTED_TOKENS = [(VALUE)]

class BY(Token):
    EXPECTED_TOKENS = [(VALUE)]

class PRINT(Token):

    RESOLUTION_ORDER = [1, 0]
    EXPECTED_TOKENS = [(ANYTYPE)]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        print(value.value)

class ADD(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (ASSIGN_R), (VARNAME)]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value += value.value

class SUBTRACT(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (FROM), (VARNAME)]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value -= value.value

class MULTIPLY(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (TIMES), (VALUE)]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value *= value.value

class DIVIDE(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (BY), (VALUE)]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value /= value.value
        if variable.value == int(variable.value):
            variable.value = int(variable.value)

class IT(VALUE):
    def _run(self, interpreter):
        variable = interpreter.get_variable('it')
        interpreter.stack_append(variable)

class LINEBREAK(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def pop_tokens(self, tokens):
        tokens.pop(0)

class COMMENT(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def pop_tokens(self, tokens):
        while tokens:
            token = tokens.pop(0)
            if isinstance(token, LINEBREAK):
                break

class AND(LINEBREAK):
    EXPECTED_TOKENS = [(ANYTYPE)]

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
          '\n': LINEBREAK}

regex_tokens = {r'^\d+$': INTEGER,
                r'^\w+$': VARNAME,
                r'^\d+\.\d+': FLOAT,
                r'^#.+?': COMMENT,
                }
