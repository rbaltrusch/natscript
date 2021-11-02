# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:53 2020

@author: Korean_Crimson
"""

import re
from token_ import tokens, keys
from token_ import regex_tokens, regex_keys

class LexError(Exception):
    def __init__(self, line_number, token):
        self.message = f'Line {line_number}: {token} was not expected at this time!'
        super().__init__(self.message)

class Lexer:
    def __init__(self):
        self.regex_patterns = [(re.compile(k), k) for k in regex_keys]

    def lex(self, string):
        string = string.replace('\n',' \n ')
        split = string.split(' ')
        for token in split:
            if token in keys:
                yield tokens[token](None)
            else:
                for pattern, key in self.regex_patterns:
                    if pattern.search(token):
                        yield regex_tokens[key](token)
                        break
                else:
                    if not token:
                        continue
                    raise LexError(token)
