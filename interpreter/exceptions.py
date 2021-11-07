# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 22:59:11 2021

@author: richa
"""

class LexError(Exception):
    def __init__(self, string, line_number):
        super().__init__(f'Line {line_number}: {string} was not expected at this time!')

class ParseException(Exception):
    def __init__(self, token):
        super().__init__(f'{token} was not expected at this location!')

class SyntaxException(Exception):
    def __init__(self, token):
        missing_tokens = [t.__name__ for t in token.EXPECTED_TOKENS[len(token.tokens):]]
        super().__init__(f'{token} cannot be run: missing expected tokens {missing_tokens}')

class UnexpectedIndentationException(Exception):
    def __init__(self, token):
        super().__init__(f'Unexpected indentation at location {token}!')

class UndefinedVariableException(Exception):
    def __init__(self, name):
        super().__init__(f'Tried to access undefined variable {name}!')

class InternalParseTypeError(Exception):
    def __init__(self, token, types):
        super().__init__(f'Expected {types=}, but got {token}!')

class InternalEmptyStackError(Exception):
    def __init__(self):
        super().__init__('Could not pop value from empty stack!')
