# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""

from typing import List

import exceptions

class Block:
    def __init__(self):
        self.tokens = []
        self.expected_tokens = None

    def __repr__(self):
        type_ = 'Block' if self.parent else 'SyntaxTree'
        return f'{type_}{self.tokens}'

    def __iter__(self):
        tokens = (self.tokens[i] for i in self.RESOLUTION_ORDER) if self.RESOLUTION_ORDER else self.tokens
        for token in tokens:
            yield token

    def run(self, interpreter):
        for token in self:
            token.run(interpreter)

    def add(self, token):
        if self.full:
            raise exceptions.InternalParseError(token)

        if not self.tokens:
            self._add_initial_token(token)
            return

        types = self.expected_tokens.pop(0)
        if not token.check_match(types):
            raise exceptions.ParseTypeError(token, types)
        self.tokens.append(token)

    def _add_initial_token(self, token):
        self.expected_tokens = token.EXPECTED_TOKENS.copy()
        self.tokens.append(token)

    @property
    def full(self) -> bool:
        return self.tokens and not self.expected_tokens

    @property
    def RESOLUTION_ORDER(self) -> List[int]:
        return self.tokens[0].RESOLUTION_ORDER if self.tokens else None

class Parser:
    def __init__(self):
        self.blocks = []

    def parse(self, tokens):
        current_block = Block()
        while tokens:
            self._pop_leading_tokens(tokens)
            if current_block.full:
                yield current_block
                current_block = Block()
            else:
                token = tokens.pop(0)
                current_block.add(token)

    def _pop_leading_tokens(self, tokens):
        while tokens:
            popped_tokens = tokens[0].pop_tokens(tokens)
            if not popped_tokens:
                break
