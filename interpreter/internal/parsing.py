# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""
from typing import Generator
from typing import List

from internal.interfaces import Token


# pylint: disable=too-few-public-methods
class Parser:
    """Parser classes, parses a list of Token objects and constructs
    token trees from them by nesting them as required.
    """

    def __init__(self):
        self.token_stack = []

    def parse(self, tokens: List[Token]) -> Generator[Token, Token, None]:
        """Constructs nested token trees by parsing the passed tokens"""
        while tokens:
            popped_tokens = tokens[0].pop_tokens(tokens) # type: ignore
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
