# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 22:59:11 2021

@author: richa
"""
from typing import List
from typing import Optional
from typing import Tuple

from interpreter.internal.interfaces import Token
from interpreter.util.pattern_matching import determine_patterns


class LexError(Exception):
    """Exception raised by Lexer"""

    def __init__(self, string, line_number):
        super().__init__(f"Line {line_number}: {string} was not expected at this time!")


class ParseException(Exception):
    """Exception raised by Parser"""

    def __init__(self, token):
        super().__init__(f"{token} was not expected at this location!")


class ParseTypeError(Exception):
    """Raised for mismatching token types"""

    def __init__(self, token: Token, types: Tuple):
        types_ = tuple([t.__name__ for t in types])
        super().__init__(f"Unexpected token at {token}, expected any of the token types {types_}.")


class InternalFullTokenParseError(Exception):
    """Internal exception - should only occur when a programming mistake was made"""

    def __init__(self, token: Token):
        super().__init__(f"Token {token=} is already full!")



class RunTimeException(Exception):
    """Base class for exceptions raised while running the program"""

    def __init__(self, *args, token: Optional[Token] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_stack: List[Token] = []
        if token is not None:
            self.token_stack.append(token)

    def __str__(self):
        return super().__str__() + self.stack_trace

    def __repr__(self):
        return super().__repr__() + self.stack_trace

    @property
    def stack_trace(self) -> str:
        """The text displaying the line number"""
        token_representations = [repr(token) for token in self.token_stack]
        patterns = determine_patterns(token_representations)
        for pattern in patterns:
            pattern.delay_start()  # we want to show the first repetition

        trace = "\n\t"
        for i, token in enumerate(token_representations):
            if not patterns:
                trace += "\n\t" + token
                continue

            pattern = patterns[0]
            if i in pattern.range:
                continue

            if i >= pattern.end:
                repeat_message = (
                    "once more..."
                    if pattern.repetitions == 1
                    else f"{pattern.repetitions} more times..."
                )
                tokens_message = (
                    "token repeats"
                    if pattern.length == 1
                    else f"{pattern.length} tokens repeat"
                )
                trace += f"\n\t[The previous {tokens_message} {repeat_message}]"
                patterns.pop(0)
            trace += "\n\t" + token
        return trace


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


class ImportException(RunTimeException):
    """Exception to be raised when something cannot be imported"""


class SyntaxException(RunTimeException):
    """Exception to be raised for syntax errors"""

    def __init__(self, token: Token):
        missing_tokens = [
            t.__name__
            for exp in token.EXPECTED_TOKENS[len(token.tokens) :]
            for t in exp.types
        ]

        if missing_tokens:
            message = f"Token is missing expected tokens {missing_tokens}"
        else:
            message = f"Did not expect token {token} at this location!"
        super().__init__(message)


class UnclosedClauseException(RunTimeException):
    """Exception to be raised for claused with unmatched close tokens"""

    def __init__(self, token: Token):
        super().__init__("Clause token was not closed with corresponding token!", token=token)


class EmptyStackError(RunTimeException):
    """Exception to be raised when trying to access a value from an empty interpreter stack"""

    def __init__(self):
        super().__init__("Expected value is missing!")
