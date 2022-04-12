# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
from interpreter import interpreter
from interpreter import lexer
from interpreter import parsing
from interpreter import token_
from tokens_ import tokens


def interpret(code: str):
    token_factory = token_.TokenFactory(tokens.get_tokens(), tokens.get_regex_tokens())
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()
    inter = interpreter.Interpreter()

    tokens_ = list(lex.lex(code))
    for syntax_block in parser.parse(tokens_):
        inter.interpret(syntax_block)
