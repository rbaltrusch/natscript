# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""

from typing import List

class Token:

    RESOLUTION_ORDER: List[int] = []
    EXPECTED_TOKENS: List[tuple] = []

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        value = '' if self.value is None else f', {self.value}'
        return f'Token({self.__class__.__name__}{value})'

    def run(self, interpreter):
        pass

    def pop(self, tokens):
        pass

class ANYTYPE(Token):
    EXPECTED_TOKENS = None

class VALUE(Token):

    EXPECTED_TOKENS = [(ANYTYPE)]

    def run(self, interpreter):
        value = interpreter.variables.get(self.value, self.value)
        interpreter.stack.append(value)

class INTEGER(VALUE):

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = int(value)

class FLOAT(VALUE):

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = float(value)

class VARNAME(VALUE):
    def run(self, interpreter):
        interpreter.stack.append(self.value)
        interpreter.variables['it'] = self.value

class ASSIGN_R(Token):
    EXPECTED_TOKENS = [(VALUE)]

class ASSIGN_L(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (ASSIGN_R), (VALUE)]

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.stack.pop()
        interpreter.variables[varname] = value

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
        value = interpreter.pop()
        print(value)

class ADD(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (ASSIGN_R), (VARNAME)]

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.pop()
        interpreter.variables[varname] += value

class SUBTRACT(Token):

    RESOLUTION_ORDER = [1, 3, 0]
    EXPECTED_TOKENS = [(VALUE), (FROM), (VARNAME)]

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.pop()
        interpreter.variables[varname] -= value

class MULTIPLY(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (TIMES), (VALUE)]

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.stack.pop()
        interpreter.variables[varname] *= value

class DIVIDE(Token):

    RESOLUTION_ORDER = [3, 1, 0]
    EXPECTED_TOKENS = [(VARNAME), (BY), (VALUE)]

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.stack.pop()
        interpreter.variables[varname] /= value
        if interpreter.variables[varname] == int(interpreter.variables[varname]):
            interpreter.variables[varname] = int(interpreter.variables[varname])

class IT(VALUE):
    def run(self, interpreter):
        variable = interpreter.variables['it']
        value = interpreter.variables[variable]
        interpreter.stack.append(value)

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

keys = tokens.keys()
regex_keys = regex_tokens.keys()
