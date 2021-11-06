# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 22:59:11 2021

@author: richa
"""

class LexError(Exception):
    def __init__(self, line_number, token):
        self.message = f'Line {line_number}: {token} was not expected at this time!'
        super().__init__(self.message)

class ParseException(Exception):
    def __init__(self, token):
        super().__init__(f'{token} was not expected at this location!')

class UndefinedVariableException(Exception):
    def __init__(self, name):
        super().__init__(f'Tried to access undefined variable {name}!')

class InternalParseTypeError(Exception):
    def __init__(self, token, types):
        super().__init__(f'Expected {types=}, but got {token}!')

class InternalEmptyStackError(Exception):
    def __init__(self):
        self.message = 'Could not pop value from empty stack!'
        super().__init__(self.message)
