# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""
from dataclasses import dataclass
from typing import Generator, List

from interpreter.internal import exceptions
from interpreter.internal.interfaces import Token


@dataclass
class TokenStack:
    """TokenStack class"""

    def __post_init__(self):
        self.tokens: List[Token] = []

    def pop(self, index=-1) -> Token:
        """Pops the element at the idex from the list"""
        return self.tokens.pop(index)

    def append(self, token: Token) -> None:
        """Appends the element to the list"""
        if token.must_be_subtoken and not token.is_subtoken:
            raise exceptions.ParseException(token)
        self.tokens.append(token)

    def __bool__(self):
        return bool(self.tokens)

    def __getitem__(self, index) -> Token:
        return self.tokens[index]


# pylint: disable=too-few-public-methods
class Parser:
    """Parser classes, parses a list of Token objects and constructs
    token trees from them by nesting them as required.
    """

    def __init__(self):
        self.token_stack = TokenStack()

    def parse(self, tokens: List[Token]) -> Generator[Token, Token, None]:
        """Constructs nested token trees by parsing the passed tokens"""
        while tokens:
            popped_tokens = tokens[0].pop_tokens(tokens)  # type: ignore
            if popped_tokens:
                continue

            token = tokens.pop(0)
            if not self.token_stack:
                self.token_stack.append(token)
                continue

            while (
                self.token_stack
                and not self._can_add(token)
                and self.token_stack[-1].is_subtoken
            ):
                self.token_stack.pop()

            if self.token_stack:
                if self._can_add(token):
                    self.token_stack[-1].add_token(token)
                else:
                    popped_token = self.token_stack.pop()
                    if not popped_token.is_subtoken:
                        yield popped_token
            self.token_stack.append(token)

            while self.token_stack[-1].full:
                token = self.token_stack.pop()
                if not self.token_stack:
                    yield token
                    break

        while self.token_stack:
            popped_token = self.token_stack.pop()
            if not popped_token.is_subtoken:
                yield popped_token

    def _can_add(self, token: Token) -> bool:
        parent = self.token_stack[-1]
        return not parent.satisfied or parent.check_optional_token(token)
