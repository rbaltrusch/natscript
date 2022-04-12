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


class RunTimeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = 1

    def __str__(self):
        return self.line_text + super().__str__()

    def __repr__(self):
        return self.line_text + super().__repr__()

    @property
    def line_text(self):
        return f'Line {self.line}: '

class SyntaxException(RunTimeException):
    def __init__(self, token):
        missing_tokens = [t.__name__ for exp in token.EXPECTED_TOKENS[len(token.tokens):] for t in exp.types]
        super().__init__(f'{token} cannot be run: missing expected tokens {missing_tokens}')

class UnexpectedIndentationException(RunTimeException):
    def __init__(self, token):
        super().__init__(f'Unexpected indentation at location {token}!')

class UndefinedVariableException(RunTimeException):
    def __init__(self, name):
        super().__init__(f'Tried to access undefined variable {name}!')


class InternalParseTypeError(Exception):
    def __init__(self, token, types):
        super().__init__(f'Expected {types=}, but got {token}!')

class InternalFullTokenParseError(Exception):
    def __init__(self, token):
        super().__init__(f'Token {token=} is already full!')

class InternalEmptyStackError(Exception):
    def __init__(self):
        super().__init__('Could not pop value from empty stack!')
