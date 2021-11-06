# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:53 2020

@author: Korean_Crimson
"""

class Lexer:
    def __init__(self, token_factory):
        self.token_factory = token_factory

    def lex(self, string):
        return (self.token_factory.create_token(s) for s in self._split(string))

    @staticmethod
    def _split(string):
        string = string.replace('\n',' \n ').strip()
        string_tokens = [s for s in string.split(' ') if s != '']
        return string_tokens
