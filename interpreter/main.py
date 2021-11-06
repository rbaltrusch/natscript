# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:26 2020

@author: Korean_Crimson
"""

from lexer import Lexer
from parser_ import Parser
from interpreter import Interpreter

lex = Lexer()
parser = Parser()
inter = Interpreter()

filename = 'test.nat'

with open(filename) as file:
    file_contents = file.read()
    tokens = list(lex.lex(file_contents))
    for syntax_block in parser.parse(tokens):
        inter.interpret(syntax_block)
