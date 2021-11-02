# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""

from typing import List

from token_ import ANYTYPE, NEW_BLOCK, LINEBREAK

class Block:
    def __init__(self, parent=None):
        self.tokens = []
        self.expected_tokens = None
        self.parent = parent

    def __repr__(self):
        type_ = 'Block' if self.parent else 'SyntaxTree'
        return f'{type_}{self.tokens}'

    def __iter__(self):
        for token in self.tokens:
            yield token

    def __getitem__(self, index):
        return self.tokens[index]

    def add(self, token):
        if self.full:
            raise ParseError(token)

        if not self.tokens:
            self._add_initial_token(token)
            return

        types = self.expected_tokens.pop(0)
        if types == (ANYTYPE) or isinstance(token, types):
            self._add_token(token)
        else:
            raise ParseTypeError(token, types)

    def _add_initial_token(self, token):
        self.expected_tokens = token.expected_tokens
        self._add_token(token)

    def _add_token(self, token):
        if isinstance(token, NEW_BLOCK):
            block = Block(parent=self)
            self.tokens.append(block)
            block.add(token)
        else:
            self.tokens.append(token)

    @property
    def full(self) -> bool:
        return self.tokens and not self.expected_tokens

    @property
    def RESOLUTION_ORDER(self) -> List[int]:
        return self.tokens[0].RESOLUTION_ORDER if self.tokens else None

class ParseError(Exception):
    def __init__(self, token):
        super().__init__(f'{token} was not expected at this location!')

class ParseTypeError(Exception):
    def __init__(self, token, types):
        super().__init__(f'Expected {types=}, but got {token}!')

class Parser:
    def __init__(self):
        self.blocks = []

    @staticmethod
    def _remove_leading_line_breaks(tokens):
        while tokens:
            #remove leading line breaks
            if isinstance(tokens[0], LINEBREAK):
                tokens.pop(0)
            else:
                break
        return tokens

    def parse(self, tokens):
        global current_block
        while tokens:
            tokens = self._remove_leading_line_breaks(tokens)
            while not current_block.full and tokens:
                token = tokens.pop(0)
                current_block.add(token)
                if current_block.full and current_block.parent:
                    current_block = current_block.parent
            yield current_block
            current_block = Block()

current_block = Block()
