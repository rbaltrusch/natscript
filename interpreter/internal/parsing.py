# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:34:15 2020

@author: Korean_Crimson
"""

class Parser:
    def __init__(self):
        self.token_stack = []

    def parse(self, tokens):
        while tokens:
            popped_tokens = tokens[0].pop_tokens(tokens)
            if popped_tokens:
                continue

            token = tokens.pop(0)
            if not self.token_stack:
                self.token_stack.append(token)
                continue

            while self.token_stack and not self._can_add(token) and self.token_stack[-1].is_subtoken:
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
            yield self.token_stack.pop()

    def _can_add(self, token):
        return not self.token_stack[-1].satisfied or self.token_stack[-1].check_optional_token(token)
