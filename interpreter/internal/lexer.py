# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:51:53 2020

@author: Korean_Crimson
"""
import re
import uuid
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
        # find all strings inside the input string and replace them by unique identifiers
        strings = re.findall(r'".*?"', string, flags=re.DOTALL)
        string_uuids = {x: str(uuid.uuid4()).replace("-", "") for x in strings}
        uuid_strings = {v: k for k, v in string_uuids.items()}
        for str_, uuid_ in string_uuids.items():
            string = string.replace(str_, f" {uuid_} ")

        string = string.replace("\n", " \n ")

        # add whitespace around [] {} , #
        string = re.sub(r"(?P<match>[\[\]\{\}\,\#])", r" \g<match> ", string).strip()

        # split unless surrounded by double quotes (i.e. a string)
        string_tokens = [uuid_strings.get(s, s) for s in string.split(" ") if s != ""]
        return string_tokens
