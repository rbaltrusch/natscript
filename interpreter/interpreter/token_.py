# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 12:04:45 2021

@author: richa
"""
import re
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import List
from typing import Tuple

from interpreter import exceptions


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
        if value is None:
            return NoneValue()

        if isinstance(value, str):
            return Value(value)

        try:
            iter(value)
            return IterableValue(value)
        except TypeError:
            return Value(value)

@dataclass
class ExpectedToken:
    types: Tuple[type]
    run_order: int = 0
    optional: bool = False

class Token:

    EXPECTED_TOKENS: List[ExpectedToken] = []
    VALUE_FACTORY: callable = None
    TOKEN_FACTORY: TokenFactory = TokenFactory()

    def __init__(self, value=None, line: int = 0):
        self.value = value
        self.line = line
        self.tokens = []
        self.run_order = 0
        self.parent = None
        self.expected_tokens = self.EXPECTED_TOKENS.copy()

    def __repr__(self):
        value = '' if self.value is None else f', {self.value}'
        type_ = 'Token' if not self.tokens else 'SyntaxTree'
        return f'Line {self.line}: {type_}({self.__class__.__name__}{value})'

    def run(self, interpreter):
        for function in self.run_functions:
            function(interpreter)

    def _run(self, interpreter):
        pass

    def check_optional_token(self, token) -> bool:
        all_types = tuple(t for token in self.expected_tokens for t in token.types)
        return isinstance(token, all_types)

    def add_token(self, token):
        if self.full:
            raise exceptions.InternalParseError(token)
        self._check_types(token)
        self.tokens.append(token)
        token.parent = self

    def pop_tokens(self, tokens):
        pass

    def update_token_factory(self, token_factory):
        pass

    def _check_types(self, token):
        while self.expected_tokens:
            expected_token = self.expected_tokens.pop(0)
            if isinstance(token, expected_token.types):
                token.run_order = expected_token.run_order
                return

            if not expected_token.optional:
                raise exceptions.InternalParseTypeError(token, expected_token.types)
        raise exceptions.ParseException(token)

    @property
    def is_subtoken(self) -> bool:
        return self.parent is not None

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
        return not self.expected_tokens

    @property
    def satisfied(self) -> bool:
        mandatory_tokens = [token for token in self.expected_tokens if not token.optional]
        return not mandatory_tokens

    @property
    def has_all_optionals(self) -> bool:
        return len(self.tokens) == len(self.EXPECTED_TOKENS)

    @property
    def run_functions(self) -> List[callable]:
        return [t.run for t in sorted(self.tokens, key=lambda x: x.run_order)] + [self._run]


class ClauseToken(Token):

    CLOSE_TOKEN = Token
    EXPECTED_TOKENS = [ExpectedToken((Token, ))] * 1000

    @property
    def full(self) -> bool:
        return self.tokens and isinstance(self.tokens[-1], self.CLOSE_TOKEN)

    @property
    def satisfied(self) -> bool:
        return self.full


@dataclass
class Value:
    value: Any = None

    def __post_init__(self):
        self.inputs = []

    def get_value(self):
        if self.value is None:
            raise exceptions.UndefinedVariableException(self)
        return self.value

    def negate_value(self) -> None:
        self.value = not self.value

    def __repr__(self):
        return str(self.value)


class IterableValue(Value):
    def get_value(self):
        return [x.get_value() for x in self.value]


class NoneValue(Value):
    def get_value(self):
        return None


class Variable(Value):
    def __init__(self, name: str):
        self.name = name
        self.inputs = []

    def __repr__(self):
        return f'{self.name}'
