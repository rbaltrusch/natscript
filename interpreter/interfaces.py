# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 13:44:51 2021

@author: richa
"""

from __future__ import annotations

from typing import Protocol, List, Dict, Optional, Any


class Token(Protocol):
    value: Any
    full: bool
    RESOLUTION_ORDER: List[int]
    EXPECTED_TOKENS: List[tuple]
    VALUE_FACTORY: Optional[callable]
    TOKEN_FACTORY: TokenFactory

    def run(self, interpreter: Interpreter) -> None:
        ...

    def add_token(self, token: Token) -> None:
        ...

    def pop_tokens(self, tokens: List[Token]) -> None:
        ...

    def update_token_factory(self, token_factory: TokenFactory) -> None:
        ...


class Value(Protocol):
    value: Any

    def get_value(self) -> Any:
        ...


class Variable(Protocol):
    value: Any
    name: str

    def get_value(self) -> Any:
        ...


class TokenFactory(Protocol):
    tokens: Dict[str, Token]
    regex_tokens: Dict[str, Token]

    def create_token(self, token: str) -> Token:
        ...

    @staticmethod
    def create_variable(name: str) -> Variable:
        ...

    @staticmethod
    def create_value(value: str) -> Value:
        ...


class Interpreter(Protocol):
    def interpret(self, token: Token) -> None:
        ...

    def add_stack(self) -> None:
        ...

    def remove_stack(self) -> None:
        ...

    def stack_pop(self) -> Any:
        ...

    def stack_append(self, value: Any) -> None:
        ...

    def check_variable(self, name: str) -> bool:
        ...

    def get_variable(self, name: str) -> Variable:
        ...

    def set_variable(self, name: str, value: Any) -> None:
        ...
