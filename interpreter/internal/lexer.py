# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:53 2020

@author: Korean_Crimson
"""
import re
from typing import Generator, List

from interpreter.internal.interfaces import Token, TokenFactory


# pylint: disable=too-few-public-methods
class Lexer:
    """Lexer class, lexes a string and turns it into a list of tokens"""

    def __init__(self, token_factory: TokenFactory):
        self.token_factory = token_factory

    def lex(self, string: str) -> Generator[Token, str, None]:
        """Turns the string into a Token generator"""
        for substring in self._split(string):
            token = self.token_factory.create_token(substring)
            token.update_token_factory(self.token_factory)
            yield token

    @staticmethod
    def _split(string: str) -> List[str]:
        string = string.replace("\n", " \n ")

        # matches non-word characters (i.e. punctuation) and adds whitespace around them
        # ignore dot (.) and quotation marks (""), needed for float and string values.
        # string = re.sub(r'(?P<match>[^\w\."])', r" \g<match> ", string).strip()

        # add whitespace around [] {} , #
        string = re.sub(r"(?P<match>[\[\]\{\}\,\#])", r" \g<match> ", string).strip()
        string_tokens = [s for s in string.split(" ") if s != ""]
        return string_tokens
