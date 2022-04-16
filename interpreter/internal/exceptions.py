# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 22:59:11 2021

@author: richa
"""
from typing import Tuple

from internal.interfaces import Token


class LexError(Exception):
    """Exception raised by Lexer"""

    def __init__(self, string, line_number):
        super().__init__(f"Line {line_number}: {string} was not expected at this time!")


class ParseException(Exception):
    """Exception raised by Parser"""

    def __init__(self, token):
        super().__init__(f"{token} was not expected at this location!")


class RunTimeException(Exception):
    """Base class for exceptions raised while running the program"""

    def __init__(self, *args, line: int = 1, **kwargs):
        super().__init__(*args, **kwargs)
        self.line = line

    def __str__(self):
        return self.line_text + super().__str__()

    def __repr__(self):
        return self.line_text + super().__repr__()

    @property
    def line_text(self) -> str:
        """The text displaying the line number"""
        return f"Line {self.line}: "


class UndefinedVariableException(RunTimeException):
    """Exception to be raised when trying to access undefined variables"""

    def __init__(self, name: str):
        super().__init__(f"Tried to access undefined variable {name}!")


class ReturnException(RunTimeException):
    """Exception to be raised by a RETURN token and caught by a CALL token"""

    def __init__(self, token: Token):
        super().__init__(f"Did not expect token {token} at this location!")


class SkipElementException(RunTimeException):
    """Exception raised by SKIP element, caught by FOR token"""

    def __init__(self, token: Token):
        super().__init__(f"Did not expect token {token} at this location!")


class BreakIterationException(RunTimeException):
    """Exception raised by BREAK element, caught by WHILE and FOR loops"""

    def __init__(self, token: Token):
        super().__init__(f"Did not expect token {token} at this location!")


class SyntaxException(RunTimeException):
    """Exception to be raised for syntax errors"""

    def __init__(self, token: Token):
        missing_tokens = [
            t.__name__
            for exp in token.EXPECTED_TOKENS[len(token.tokens) :]
            for t in exp.types
        ]
        super().__init__(
            f"{token} cannot be run: missing expected tokens {missing_tokens}"
        )


class ParseTypeError(Exception):
    """Raised for mismatching token types"""

    def __init__(self, token: Token, types: Tuple):
        super().__init__(f"Expected {types=}, but got {token}!")


class EmptyStackError(Exception):
    """Internal exception - should only occur when a programming mistake was made"""

    def __init__(self):
        super().__init__("Could not pop value from empty stack!")


class InternalFullTokenParseError(Exception):
    """Internal exception - should only occur when a programming mistake was made"""

    def __init__(self, token: Token):
        super().__init__(f"Token {token=} is already full!")
