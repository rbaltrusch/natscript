# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 12:04:45 2021

@author: richa
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from internal import exceptions
from internal import tokenvalue
from internal.interfaces import Interpreter

# pylint: disable=no-self-use
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


@dataclass
class TokenFactory:

    tokens: Dict[str, Type[Token]] = field(default_factory=dict)
    regex_tokens: Dict[str, Type[Token]] = field(default_factory=dict)

    def __post_init__(self):
        self._regex_patterns = [(re.compile(k), k) for k in self.regex_tokens]
        self.line_number = 1
        self._value_cache = {}
        self._none_value = tokenvalue.NoneValue()

    def create_token(self, token: str) -> Token:
        if token in self.tokens:
            token_type = self.tokens[token]
            return token_type(value=None, line=self.line_number)

        for pattern, key in self._regex_patterns:
            if pattern.search(token):
                token_type = self.regex_tokens[key]
                return token_type(value=token, line=self.line_number)

        raise exceptions.LexError(token, self.line_number)

    @staticmethod
    def create_variable(name: str) -> tokenvalue.Variable:
        return tokenvalue.Variable(name)

    def create_any_value(self, value: Any) -> tokenvalue.Value:
        if value is None:
            return self.create_none_value()

        try:
            return self.create_value(value)
        except TypeError:
            return self.create_iterable_value(value)

    def create_value(self, value: Any) -> tokenvalue.Value:
        return self._value_cache.get(value, tokenvalue.Value(value))

    @staticmethod
    def create_iterable_value(value: Iterable) -> tokenvalue.IterableValue:
        return tokenvalue.IterableValue(value)

    def create_none_value(self) -> tokenvalue.NoneValue:
        return self._none_value


@dataclass
class ExpectedToken:
    types: Tuple[Type[Token], ...]
    run_order: int = 0
    optional: bool = False

    def pop_token_from(self, expected_tokens: List[ExpectedToken]) -> ExpectedToken:
        return expected_tokens.pop(0)

    def copy(self) -> ExpectedToken:
        return self

    @property
    def needs_copy(self) -> bool:
        return False


class ExpectedTokenCombination:
    def __init__(self, *tokens: ExpectedToken, optional=False, copied=False):
        self.tokens = list(tokens)
        self.optional = optional
        self.copied = copied

    def pop_token_from(self, expected_tokens: List[ExpectedToken]):
        tokens = self.tokens if self.tokens else expected_tokens
        return tokens.pop(0)

    def copy(self):
        return self.__class__(*self.tokens, optional=self.optional, copied=True)

    @property
    def needs_copy(self) -> bool:
        return not self.copied

    @property
    def types(self) -> Tuple[Type[Token], ...]:
        types: List[Type[Token]] = []
        for token in self.tokens:
            types.extend(token.types)
            if not token.optional:
                break
        return tuple(types)

    @property
    def run_order(self) -> int:
        if not self.tokens:
            return 0
        return self.tokens[0].run_order


class Token:

    EXPECTED_TOKENS: List[ExpectedToken] = []
    VALUE_FACTORY: Optional[Callable[..., Any]] = None
    TOKEN_FACTORY: TokenFactory = TokenFactory()
    TOKEN_STACK: List[Token] = []
    functional = True

    def __init__(self, value: Optional[Any] = None, line: int = 0):
        self.value = value
        self.line = line
        self.tokens: List[Token] = []
        self.run_order = 0
        self.parent: Optional[Token] = None
        self.expected_tokens = self.EXPECTED_TOKENS[:]
        self._sorted_tokens = None

    def __repr__(self):
        value = '' if self.value is None else f', {self.value}'
        type_ = 'Token' if not self.tokens else 'SyntaxTree'
        return f'Line {self.line}: {type_}({self.__class__.__name__}{value})'

    def init(self, interpreter):
        for token in self.tokens:
            if token.functional:
                token.init(interpreter)
        self._init(interpreter)

    def _init(self, interpreter):
        pass

    def run(self, interpreter):
        if self._sorted_tokens is None:
            self._sorted_tokens = sorted(
                [x for x in self.tokens if x.functional], key=lambda x: x.run_order
            )

        for token in self._sorted_tokens:
            token.run(interpreter)
        self._run(interpreter)

    def _run(self, _: Interpreter):
        pass

    def check_optional_token(self, token: Token) -> bool:
        all_types = tuple(t for token in self.expected_tokens for t in token.types)
        return isinstance(token, all_types)

    def add_token(self, token: Token):
        if self.full:
            raise exceptions.InternalFullTokenParseError(token)
        self._check_types(token)
        self.tokens.append(token)
        token.parent = self

    def pop_tokens(self, _: List[Token]):
        pass

    def update_token_factory(self, _: TokenFactory):
        pass

    @classmethod
    def print_token_stack(cls):
        print('---TOKEN STACK---')
        for token in cls.TOKEN_STACK:
            print(token)

    def _check_types(self, token: Token):
        while self.expected_tokens:
            if self.expected_tokens[0].needs_copy:
                self.expected_tokens[0] = self.expected_tokens[0].copy()
            expected_token = self.expected_tokens[0].pop_token_from(self.expected_tokens)
            if isinstance(token, expected_token.types):
                token.run_order = expected_token.run_order
                return

            if not expected_token.optional:
                raise exceptions.ParseTypeError(token, expected_token.types)
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
            self._value = self.VALUE_FACTORY(value) # pylint: disable=not-callable
        else:
            self._value = value

    @property
    def full(self) -> bool:
        return not self.expected_tokens

    @property
    def satisfied(self) -> bool:
        mandatory_tokens = [token for token in self.expected_tokens if not token.optional]
        return not mandatory_tokens

    @cached_property
    def has_all_optionals(self) -> bool:
        return len(self.tokens) == len(self.EXPECTED_TOKENS)


class ClauseToken(Token):

    CLOSE_TOKEN = Token
    EXPECTED_TOKENS = [ExpectedToken((Token, ))] * 1000

    @property
    def full(self) -> bool:
        return bool(self.tokens) and isinstance(self.tokens[-1], self.CLOSE_TOKEN)

    @property
    def satisfied(self) -> bool:
        return self.full


class SkipToken(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)
