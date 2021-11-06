# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:26 2020

@author: Korean_Crimson
"""

import token_
import tokens
import lexer
import parsing
import interpreter

token_factory = token_.TokenFactory(tokens.tokens, tokens.regex_tokens)
lex = lexer.Lexer(token_factory)
parser = parsing.Parser()
inter = interpreter.Interpreter()

filename = 'test.nat'

with open(filename) as file:
    file_contents = file.read()
    tokens = list(lex.lex(file_contents))
    for syntax_block in parser.parse(tokens):
        inter.interpret(syntax_block)
