# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""

from typing import List

from token_ import ANYTYPE, NEW_BLOCK, LINEBREAK

class Block:
    def __init__(self, parent=None):
        self.current_tokens = 0
        self.tokens = []
        self.length = None
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

    def _add_token(self, token):
        self.current_tokens += 1
        if isinstance(token, NEW_BLOCK):
            block = Block(parent=self)
            self.tokens.append(block)
            block.add(token)
        else:
            self.tokens.append(token)

    def add(self, token):
        if self.length is None:
            #initial element add
            self.length = len(token.expected_tokens) + 1 #2 = 1 extra because of self
            self.expected_tokens = token.expected_tokens
            self._add_token(token)
        elif self.current_tokens < self.length:
            #subsequent elements
            types = self.expected_tokens.pop(0)
            if types == (ANYTYPE) or isinstance(token, types):
                self._add_token(token)
            else:
                raise ParseTypeError(token, types) #Type error
        else:
            raise ParseError(token) #shouldnt add more than length allows

    @property
    def full(self) -> bool:
        return len(self.tokens) == self.length if self.length else False

    @property
    def RESOLUTION_ORDER(self) -> List[int]:
        return self.tokens[0].RESOLUTION_ORDER if self.tokens else None

class ParseError(Exception):
    def __init__(self, token):
        self.message = f'{token} was not expected at this location!'
        super().__init__(self.message)

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
