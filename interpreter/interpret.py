# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""

import token_
import tokens
import lexer
import parsing
import interpreter


def interpret(code: str):
    token_factory = token_.TokenFactory(tokens.tokens, tokens.regex_tokens)
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()
    inter = interpreter.Interpreter()

    tokens_ = list(lex.lex(code))
    for syntax_block in parser.parse(tokens_):
        inter.interpret(syntax_block)
