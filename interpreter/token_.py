# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""

class Token:

    type = None

    def __init__(self, value):
        self.value = value
        self.expected_tokens = self.expect()

    def __repr__(self):
        return f'Token({self.__class__.__name__}, {self.value})'

    @staticmethod
    def expect():
        '''expected tokens is a list of lists: the primary list contains a list
        of all possible subsequent expected tokens'''
        return []

    def run(self, interpreter):
        pass

class ANYTYPE(Token):
    @staticmethod
    def expect():
        raise NotImplementedError

class ASSIGN_L(Token):

    type = "ASSIGN"

    @staticmethod
    def expect():
        list_of_expected_tokens = [(VARNAME), (ASSIGN_R), (VALUE)]
        return list_of_expected_tokens

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.stack.pop()
        interpreter.variables[varname] = value

class ASSIGN_R(Token):
    @staticmethod
    def expect():
        return [(VALUE)]

class FROM(Token):
    @staticmethod
    def expect():
        return [(VALUE)]

class TIMES(Token):
    @staticmethod
    def expect():
        return [(VALUE)]

class BY(Token):
    @staticmethod
    def expect():
        return [(VALUE)]

class VALUE(Token):
    @staticmethod
    def expect():
        return [(ANYTYPE)]

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

class NEW_BLOCK(Token):
    @staticmethod
    def expect():
        return [(ANYTYPE)]

class PRINT(Token):

    type = "PRINT"

    @staticmethod
    def expect():
        return [(ANYTYPE)]

    def run(self, interpreter):
        value = interpreter.pop()
        print(value)

class ADD(Token):

    type = "ADD"

    @staticmethod
    def expect():
        list_of_expected_tokens = [(VALUE), (ASSIGN_R), (VARNAME)]
        return list_of_expected_tokens

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.pop()
        interpreter.variables[varname] += value

class SUBTRACT(Token):

    type = "SUBTRACT"

    @staticmethod
    def expect():
        list_of_expected_tokens = [(VALUE), (FROM), (VARNAME)]
        return list_of_expected_tokens

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.pop()
        interpreter.variables[varname] -= value

class MULTIPLY(Token):

    type = "MULTIPLY"

    @staticmethod
    def expect():
        list_of_expected_tokens = [(VARNAME), (TIMES), (VALUE)]
        return list_of_expected_tokens

    def run(self, interpreter):
        varname = interpreter.stack.pop()
        value = interpreter.stack.pop()
        interpreter.variables[varname] *= value

class DIVIDE(Token):

    type = "DIVIDE"

    @staticmethod
    def expect():
        list_of_expected_tokens = [(VARNAME), (BY), (VALUE)]
        return list_of_expected_tokens

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
    @staticmethod
    def expect():
        return [(ANYTYPE)]

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
          '\n': LINEBREAK}

regex_tokens = {r'^\d+$': INTEGER,
                r'^\w+$': VARNAME,
                r'^\d+\.\d+': FLOAT,
                }

keys = tokens.keys()
regex_keys = regex_tokens.keys()

resolution_order_dict = {"ASSIGN": [3, 1, 0],
                         "PRINT": [1, 0],
                         "ADD": [1, 3, 0],
                         "SUBTRACT": [1, 3, 0],
                         "MULTIPLY": [3, 1, 0],
                         "DIVIDE": [3, 1, 0],
                         }
