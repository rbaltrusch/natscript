# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
from typing import List

from internal import interfaces
from internal import interpreter
from internal import lexer
from internal import parsing
from internal import token_
from tokens_ import compiler
from tokens_ import tokens

def construct_tokens(filename: str) -> None:
    try:
        return compiler.read_compiled_file(filename)
    except compiler.CompilerError:
        pass

    token_factory = token_.TokenFactory(tokens.get_tokens(), tokens.get_regex_tokens())
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()

    code = read_file(filename)
    tokens_ = list(lex.lex(code))
    syntax_blocks = list(parser.parse(tokens_))
    compiler.write_compiled_file(syntax_blocks, filename)
    return syntax_blocks

def interpret(syntax_blocks: List[interfaces.Token]) -> None:
    """Constructs a token tree for the source code file specified, either
    by reading the source code directly or loading the token tree from a compiled file,
    then runs all tokens in the tree.
    """
    inter = interpreter.Interpreter()
    for syntax_block in syntax_blocks:
        syntax_block.init(inter)

    for syntax_block in syntax_blocks:
        inter.interpret(syntax_block)


def read_file(filename: str) -> str:
    """Reads the specified file and returns its contents"""
    with open(filename, "r", encoding="utf-8") as file:
        file_contents = file.read()
    return file_contents


def print_token_trace(token: token_.Token, indent: int = 0):
    """Recursively prints information tree for token and its subtokens."""
    values = [] if token.value is None else [token.value]
    print(token.line, ' ' * indent, token.__class__.__name__, *values)
    for token in token.tokens:
        print_token_trace(token, indent+4)
