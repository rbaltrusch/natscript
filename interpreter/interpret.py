# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

from interpreter.internal import exceptions, lexer, parsing, token_, tokenvalue
from interpreter.internal.interpreter import Interpreter
from interpreter.tokens_ import tokens
from setup import VERSION


def construct_tokens_from_string(code: str) -> List[token_.Token]:
    """Constructs a list of nested tokens from the specified code string"""
    token_factory = token_.TokenFactory(
        tokens.get_tokens(), tokens.get_regex_tokens()  # type: ignore
    )
    lex = lexer.Lexer(token_factory)
    parser = parsing.Parser()
    tokens_ = list(lex.lex(code))
    syntax_blocks = list(parser.parse(tokens_))
    return syntax_blocks  # type: ignore


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


def run_interactive_shell():
    """Opens an interactive natscript shell"""
    interpreter = Interpreter()
    print(f"Natscript interpreter interactive shell (version: {VERSION})")
    print("Type 'exit' to exit the shell.")
    add_lib_to_path()
    repl_runner = ReplRunner()
    repl_runner.run(interpreter)


def interpret(
    syntax_blocks: List[token_.Token],
    iterations: int = 1,
    interpreter: Optional[Interpreter] = None,
) -> None:
    """Runs all tokens in the specified syntax blocks.
    Note: tokens need to be grouped first by parser.
    Adds the Natscript standard library to path as a side-effect
    """
    add_lib_to_path()
    inter = interpreter or Interpreter()
    run_tokens(syntax_blocks, inter, iterations=iterations)


def run_tokens(
    syntax_blocks: List[token_.Token], interpreter: Interpreter, iterations: int = 1
):
    """Runs all tokens in the specified syntax blocks.
    Note: tokens need to be grouped first by parser.
    """
    for syntax_block in syntax_blocks:
        interpreter.init(syntax_block)

    runnables = flatten_syntax_blocks(syntax_blocks)
    for _ in range(iterations):
        for syntax_block in runnables:
            interpreter.run(syntax_block)


def add_lib_to_path():
    """Adds Natscript lib to path"""
    sys.path.insert(
        1, os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "lib")
    )


def flatten_syntax_blocks(syntax_blocks: List[token_.Token]) -> List[token_.Token]:
    """Flattens token structure where possible to avoid deep nesting and improve performance"""

    def flatten(syntax_block: token_.Token):
        # skip tokens overriding the Token.run method
        if syntax_block.run.__code__ is not token_.Token.run.__code__:
            flattened.append(syntax_block)
            return

        for child in syntax_block.sorted_tokens:
            flatten(child)
        if syntax_block.runnable:
            syntax_block.run = syntax_block._run  # pylint: disable=protected-access
            flattened.append(syntax_block)

    flattened = []
    for syntax_block in syntax_blocks:
        flatten(syntax_block)
    return flattened


def read_file(filepath: str) -> str:
    """Reads the specified file and returns its contents"""
    search_paths = get_search_paths()
    for path in search_paths:
        full_filepath = os.path.join(path, filepath)
        if not os.path.isfile(full_filepath):
            continue

        with open(full_filepath, "r", encoding="utf-8") as file:
            return file.read()
    raise FileNotFoundError from None


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


class ReplPrinter:
    """Default repl printer for interactive shell sessions
    prints out the interpreter stack values when run.
    """

    def run(self, interpreter: Interpreter) -> None:
        """Prints out the interpreter stack values when run"""
        values = list(self._get_stack_values(interpreter))
        printer = tokens.PRINT()
        printer.init(interpreter)
        for value in reversed(values):
            interpreter.stack_append(value)
            try:
                interpreter.run(printer)
            except exceptions.RunTimeException as exc:
                print(exc)
                break

    def _get_stack_values(self, interpreter: Interpreter) -> List[tokenvalue.Value]:
        """empties the interpreter stack and gets all values"""
        while True:
            try:
                yield interpreter.stack_pop()
            except exceptions.EmptyStackError:
                break


@dataclass
class ReplRunner:
    """Repl runner for interactive shell sessions"""

    printer: ReplPrinter = field(default_factory=ReplPrinter)

    def run(self, interpreter: Interpreter):
        """Runs the repl shell using the specified interpreter"""
        while True:
            tokens_ = self._read_tokens()
            if not tokens_:
                continue
            self._run_tokens(interpreter, tokens_)
            self.printer.run(interpreter)

    def _run_tokens(self, interpreter: Interpreter, tokens_: List[token_.Token]):
        try:
            run_tokens(tokens_, interpreter=interpreter)
        except exceptions.RunTimeException as exc:
            print(exc)

    def _read_tokens(self) -> Optional[List[token_.Token]]:
        line = input(">>> ")
        try:
            tokens_ = construct_tokens_from_string(line)
        except exceptions.TokenizationError as exc:
            print(exc)
            return

        if not tokens_:
            return

        while not tokens_[-1].fully_satisfied:
            line += " " + input("more? ")
            try:
                tokens_ = construct_tokens_from_string(line)
            except exceptions.TokenizationError as exc:
                tokens_ = None
                print(exc)
        return tokens_
