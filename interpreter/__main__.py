# -*- coding: utf-8 -*-
"""
The entry point to the Natscript interpreter.
"""
import argparse
import os
import sys

import interpreter.cli
from interpreter import interpret
from interpreter.internal import token_
from interpreter.tokens_ import compiler
from interpreter.util import path

argparser = interpreter.cli.construct_parser()
arguments = argparser.parse_args()
if not arguments.args:
    raise argparse.ArgumentError(
        argument="args", message="Filepath of script to be run needs to be supplied!"
    )

filepath = arguments.args[0]
sys.argv = arguments.args

if not arguments.debug:
    sys.tracebacklimit = 0

if arguments.compile == "True":
    compiler_ = (
        compiler.PickleCompiler()
        if arguments.compiled_format == "pickle"
        else compiler.JsonCompiler()
    )
    token_.Token.TOKEN_COMPILER = compiler_
    try:
        tokens = compiler_.read_compiled_file(filepath)
    except compiler.CompilerError:
        tokens = interpret.construct_tokens(filepath)
    compiler_.write_compiled_file(tokens, filepath)
else:
    tokens = interpret.construct_tokens(filepath)

if arguments.debug:
    for token in tokens:
        interpret.print_token_trace(token)

with path.ChangeDir(folder=os.path.dirname(filepath)):
    interpret.interpret(tokens, arguments.iterations)
