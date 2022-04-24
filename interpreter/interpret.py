# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
import os
from typing import List

from interpreter.internal import interpreter, lexer, parsing, token_
from interpreter.tokens_ import tokens


def construct_tokens(filepath: str) -> List[token_.Token]:
    """Reads in the source code at the filepath and returns a list of nested tokens
    constructed from the parsed code.
    """
    token_factory = token_.TokenFactory(
        tokens.get_tokens(), tokens.get_regex_tokens()  # type: ignore
    )
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()

    code = read_file(filepath)
    tokens_ = list(lex.lex(code))
    for token in tokens_:
        token.filepath = filepath

    syntax_blocks = list(parser.parse(tokens_))
    return syntax_blocks  # type: ignore


def interpret(syntax_blocks: List[token_.Token], iterations: int = 1) -> None:
    """Constructs a token tree for the source code file specified, either
    by reading the source code directly or loading the token tree from a compiled file,
    then runs all tokens in the tree.
    """
    inter = interpreter.Interpreter()
    for syntax_block in syntax_blocks:
        inter.init(syntax_block)

    for _ in range(iterations):
        for syntax_block in syntax_blocks:
            inter.run(syntax_block)


def read_file(filepath: str) -> str:
    """Reads the specified file and returns its contents"""
    search_paths = get_search_paths()
    for path in search_paths:
        full_filepath = os.path.join(path, filepath)
        if not os.path.isfile(full_filepath):
            continue

        with open(full_filepath, "r", encoding="utf-8") as file:
            return file.read()
    raise FileNotFoundError


def get_search_paths() -> List[str]:
    """Returns a list of the folders in which the interpreter will search for a specified file"""
    search_paths = [
        "",
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "lib"),
    ]
    env_path = os.getenv("NATSCRIPT_PATH")
    if env_path is not None:
        search_paths.extend(env_path.split(";"))
    return search_paths


def print_token_trace(token: token_.Token, indent: int = 0):
    """Recursively prints information tree for token and its subtokens."""
    values = [] if token.value is None else [token.value]
    print(token.line, " " * indent, token.__class__.__name__, *values)
    for token in token.tokens:
        print_token_trace(token, indent + 4)
