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
        self.line_count = 0

    def lex(self, string):
        self.line_number = 0
        string = string.replace('\n',' \n ').strip()
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
                    raise LexError(self.line_number, token)
            if token == '\n':
                self.line_number += 1
