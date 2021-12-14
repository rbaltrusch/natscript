# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:53 2020

@author: Korean_Crimson
"""
import re

class Lexer:
    def __init__(self, token_factory):
        self.token_factory = token_factory

    def lex(self, string):
        for s in self._split(string):
            token = self.token_factory.create_token(s)
            token.update_token_factory(self.token_factory)
            yield token

    @staticmethod
    def _split(string):
        string = string.replace('\n', ' \n ')

        #matches non-word characters (i.e. punctuation) and adds whitespace around them
        string = re.sub('(?P<match>[^\w\.])', ' \g<match> ', string).strip()

        string_tokens = [s for s in string.split(' ') if s != '']
        return string_tokens
