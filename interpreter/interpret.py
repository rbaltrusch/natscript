# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
from internal import parsing
from internal import lexer
from internal import interpreter
import interpreter.token_ as token
from tokens_ import tokens
from tokens_ import compiler


def interpret(filename: str):
    token_factory = token.TokenFactory(tokens.get_tokens(), tokens.get_regex_tokens())
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


def print_token_trace(token: token.Token, indent: int = 0):
    """Recursively prints information tree for token and its subtokens."""
    values = [] if token.value is None else [token.value]
    print(token.line, ' ' * indent, token.__class__.__name__, *values)
    for token in token.tokens:
        print_token_trace(token, indent+4)
