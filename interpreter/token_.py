# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 12:04:45 2021

@author: richa
"""

import re
from typing import List, Any
from dataclasses import dataclass, field

import exceptions


@dataclass
class TokenFactory:

    tokens: dict = field(default_factory=dict)
    regex_tokens: dict = field(default_factory=dict)

    def __post_init__(self):
        self.regex_patterns = [(re.compile(k), k) for k in self.regex_tokens.keys()]
        self.line_number = 1

    def create_token(self, token: str):
        if token in self.tokens:
            token_type = self.tokens[token]
            return token_type(value=None, line=self.line_number)

        for pattern, key in self.regex_patterns:
            if pattern.search(token):
                token_type = self.regex_tokens[key]
                return token_type(value=token, line=self.line_number)

        raise exceptions.LexError(token, self.line_number)

    @staticmethod
    def create_variable(name: str):
        return Variable(name)

    @staticmethod
    def create_value(value: Any):
        return Value(value)


class Token:

    RESOLUTION_ORDER: List[int] = []
    EXPECTED_TOKENS: List[tuple] = []
    VALUE_FACTORY: callable = None
    TOKEN_FACTORY: TokenFactory = TokenFactory()

    def __init__(self, value=None, line: int = 0):
        self.value = value
        self.line = line
        self.tokens = []

    def __repr__(self):
        value = '' if self.value is None else f', {self.value}'
        type_ = 'Token' if not self.tokens else 'SyntaxTree'
        return f'Line {self.line}: {type_}({self.__class__.__name__}{value})'

    def run(self, interpreter):
        for function in self.run_functions:
            function(interpreter)

    def _run(self, interpreter):
        pass

    def add_token(self, token):
        if self.full:
            raise exceptions.InternalParseError(token)

        index = len(self.tokens)
        types = self.EXPECTED_TOKENS[index]
        if not isinstance(token, types):
            raise exceptions.InternalParseTypeError(token, types)
        self.tokens.append(token)

    def pop_tokens(self, tokens):
        pass

    def update_token_factory(self, token_factory):
        pass

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.VALUE_FACTORY is not None:
            self._value = self.VALUE_FACTORY(value)
        else:
            self._value = value

    @property
    def full(self) -> bool:
        return len(self.tokens) == len(self.EXPECTED_TOKENS)

    @property
    def run_functions(self) -> List[callable]:
        if not self.RESOLUTION_ORDER:
            return [self._run]

        if not len(self.tokens) == len(self.EXPECTED_TOKENS):
            raise exceptions.SyntaxException(self)

        tokens = [self] + self.tokens
        ordered = [tokens[i] for i in self.RESOLUTION_ORDER]
        return [t._run if t is self else t.run for t in ordered]


class ClauseToken(Token):

    CLOSE_TOKEN = Token
    EXPECTED_TOKENS = [(Token, )] * 1000

    @property
    def full(self) -> bool:
        return self.tokens and isinstance(self.tokens[-1], self.CLOSE_TOKEN)


@dataclass
class Value:
    value: Any = None

    def get_value(self):
        if self.value is None:
            raise exceptions.UndefinedVariableException(self)
        return self.value

class Variable(Value):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f'{self.name}'
