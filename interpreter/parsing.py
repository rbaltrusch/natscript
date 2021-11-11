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
            self._pop_leading_tokens(tokens)
            if not tokens:
                return

            current_token = tokens.pop(0)
            self.token_stack.append(current_token)

            while self.token_stack and not self.token_stack[-1].full and tokens:
                token = tokens.pop(0)

                if not self.token_stack[-1].satisfied or self.token_stack[-1].check_optional_token(token):
                    self.token_stack[-1].add_token(token)
                else:
                    self.token_stack.append(token)

                if not token.full and token is not self.token_stack[-1]:
                    self.token_stack.append(token)

                while self.token_stack and self.token_stack[-1].full:
                    token = self.token_stack.pop()
                    if not self.token_stack:
                        yield token
                        break

        while self.token_stack and self.token_stack[1].satisfied:
            yield self.token_stack.pop()

    def _pop_leading_tokens(self, tokens):
        while tokens:
            current_token = tokens[0]
            popped_tokens = current_token.pop_tokens(tokens)
            if not popped_tokens:
                break
