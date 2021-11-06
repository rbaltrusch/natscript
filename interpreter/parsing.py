# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""

class Parser:
    def __init__(self):
        self.blocks = []

    def parse(self, tokens):
        while tokens:
            self._pop_leading_tokens(tokens)
            if not tokens:
                return

            current_token = tokens[0]
            tokens.pop(0)

            while not current_token.full and tokens:
                token = tokens.pop(0)
                current_token.add_token(token)
            yield current_token

    def _pop_leading_tokens(self, tokens):
        while tokens:
            current_token = tokens[0]
            popped_tokens = current_token.pop_tokens(tokens)
            if not popped_tokens:
                break
