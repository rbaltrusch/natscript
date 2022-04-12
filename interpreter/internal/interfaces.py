# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 13:44:51 2021

@author: richa
"""
from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Protocol


class Token(Protocol):
    """Protocol for executable Tokens"""

    value: Any
    line: int
    full: bool
    satisfied: bool
    RESOLUTION_ORDER: List[int]
    EXPECTED_TOKENS: List[tuple]
    VALUE_FACTORY: Optional[Callable[..., Any]]
    TOKEN_FACTORY: TokenFactory
    TOKEN_STACK: List[Token]

    def run(self, interpreter: Interpreter) -> None:
        """Runs the token"""

    def add_token(self, token: Token) -> None:
        """Adds the specified token to its subtokens"""

    def pop_tokens(self, tokens: List[Token]) -> None:
        """Removes any number of tokens from the passed list"""

    def update_token_factory(self, token_factory: TokenFactory) -> None:
        """Updates the token factory"""

    @classmethod
    def print_token_stack(cls):
        """Prints the current token stack"""


class Value(Protocol):
    """Protocol for interpreter stack Value objects"""

    value: Any
    inputs: Optional[List[Variable]]

    def get_value(self) -> Any:
        """Returns the actual value of the Value"""


class Variable(Protocol):
    """Protocol for interpreter Variable objects"""

    value: Any
    name: str
    inputs: Optional[List[Variable]]

    def get_value(self) -> Any:
        """Returns the actual value of the Variable"""


class TokenFactory(Protocol):
    """Protocol for TokenFactory"""

    tokens: Dict[str, Token]
    regex_tokens: Dict[str, Token]

    def create_token(self, token: str) -> Token:
        """Returns a new token"""

    @staticmethod
    def create_variable(name: str) -> Variable:
        """Returns a new Variable"""

    @staticmethod
    def create_value(value: str) -> Value:
        """Returns a new Value"""


class Interpreter(Protocol):
    """Protocol for token interpreter"""

    def interpret(self, token: Token) -> None:
        """Runs the token"""

    def add_stack(self) -> None:
        """Adds a new stack"""

    def remove_stack(self) -> None:
        """Removes the last stack"""

    def stack_pop(self) -> Any:
        """Pops the last value from the current stack"""

    def stack_append(self, value: Value) -> None:
        """Appends a value to the current stack"""

    def check_variable(self, name: str) -> bool:
        """Checks whether the specified name identifies a declared variable"""

    def get_variable(self, name: str) -> Variable:
        """Returns the value of the variable specified by name"""

    def set_variable(self, name: str, value: Variable) -> None:
        """Saves the variable specified by name and the corresponding Variable object"""
