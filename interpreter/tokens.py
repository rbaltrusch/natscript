# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""

from token_ import Token, Variable, Value, ANYTYPE

class VALUE(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def run(self, interpreter):
        value = Value(self.value)
        interpreter.stack_append(value)

class INTEGER(VALUE):
    VALUE_FACTORY = int

class FLOAT(VALUE):
    VALUE_FACTORY = float

class VARNAME(VALUE):
    def run(self, interpreter):
        if interpreter.check_variable(self.value):
            variable = interpreter.get_variable(self.value)
        else:
            variable = Variable(self.value)

        interpreter.stack_append(variable)
        interpreter.set_variable('it', variable)

class ASSIGN_R(Token):
    EXPECTED_TOKENS = [(VALUE)]

class ASSIGN_L(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (ASSIGN_R), (VALUE)]

    def run(self, interpreter):
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

    def run(self, interpreter):
        value = interpreter.stack_pop()
        print(value.value)

class ADD(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (ASSIGN_R), (VARNAME)]

    def run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value += value.value

class SUBTRACT(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (FROM), (VARNAME)]

    def run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value -= value.value

class MULTIPLY(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (TIMES), (VALUE)]

    def run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value *= value.value

class DIVIDE(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (BY), (VALUE)]

    def run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value /= value.value
        if variable.value == int(variable.value):
            variable.value = int(variable.value)

class IT(VALUE):
    def run(self, interpreter):
        variable = interpreter.get_variable('it')
        interpreter.stack_append(variable)

class LINEBREAK(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def pop(self, tokens):
        tokens.pop(0)

class COMMENT(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def pop(self, tokens):
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
          '\n': LINEBREAK}

regex_tokens = {r'^\d+$': INTEGER,
                r'^\w+$': VARNAME,
                r'^\d+\.\d+': FLOAT,
                r'^#.+?': COMMENT,
                }
