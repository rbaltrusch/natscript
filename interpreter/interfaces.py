# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 13:44:51 2021

@author: richa
"""

from __future__ import annotations

from typing import Protocol, List, Dict, Optional, Any


class Token(Protocol):
    value: Any
    RESOLUTION_ORDER: List[int]
    EXPECTED_TOKENS: List[tuple]
    VALUE_FACTORY: Optional[callable]
    TOKEN_FACTORY: TokenFactory

    def run(self, interpreter: Interpreter) -> None:
        ...

    def pop_tokens(self, tokens: List[Token]) -> None:
        ...

    def check_match(self, types: List[type]) -> bool:
        ...


class Variable(Protocol):
    value: Any
    name: str


class Value(Protocol):
    value: Any


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
    def interpret(self, block: Block) -> None:
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


class Block(Protocol):
    def run(self, interpreter: Interpreter) -> None:
        ...