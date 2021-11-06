# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 12:04:45 2021

@author: richa
"""

import re
from typing import List, Callable, Any
from dataclasses import dataclass, field

import exceptions


@dataclass
class TokenFactory:

    tokens: dict = field(default_factory=dict)
    regex_tokens: dict = field(default_factory=dict)

    def __post_init__(self):
        self.regex_patterns = [(re.compile(k), k) for k in self.regex_tokens.keys()]

    def create_token(self, token: str):
        if token in self.tokens:
            token_type = self.tokens[token]
            return token_type(value=None)

        for pattern, key in self.regex_patterns:
            if pattern.search(token):
                token_type = self.regex_tokens[key]
                return token_type(value=token)

        raise exceptions.LexError(token)

    @staticmethod
    def create_variable(name: str):
        return Variable(name)

    @staticmethod
    def create_value(value: Any):
        return Value(value)


class Token:

    RESOLUTION_ORDER: List[int] = []
    EXPECTED_TOKENS: List[tuple] = []
    VALUE_FACTORY: Callable[[Any], Any] = None
    TOKEN_FACTORY: TokenFactory = TokenFactory()

    def __init__(self, value=None):
        self.value = value

    def __repr__(self):
        value = '' if self.value is None else f', {self.value}'
        return f'Token({self.__class__.__name__}{value})'

    def run(self, interpreter):
        pass

    def pop(self, tokens):
        pass

    def check_match(self, types) -> bool:
        return types == (ANYTYPE) or isinstance(self, types)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.VALUE_FACTORY is not None:
            self._value = self.VALUE_FACTORY(value)
        else:
            self._value = value


class ANYTYPE(Token):
    EXPECTED_TOKENS = None

@dataclass
class Variable:
    name: str
    value: Any = None

@dataclass
class Value:
    value: Any = None
