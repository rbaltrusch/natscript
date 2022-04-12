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
from tokens_ import compiler


def interpret(filename: str):
    token_factory = token_.TokenFactory(tokens.get_tokens(), tokens.get_regex_tokens())
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()
    inter = interpreter.Interpreter()

    try:
        syntax_blocks = compiler.read_compiled_file(filename)
    except compiler.CompilerError:
        code = read_file(filename)
        tokens_ = list(lex.lex(code))
        syntax_blocks = list(parser.parse(tokens_))
        compiler.write_compiled_file(syntax_blocks, filename)

    for syntax_block in syntax_blocks:
        inter.interpret(syntax_block)


def read_file(filename: str):
    with open(filename) as file:
        file_contents = file.read()
    return file_contents
