# -*- coding: utf-8 -*-
"""
The entry point to the Natscript interpreter.
"""
import os
import sys

import interpreter.cli
from interpreter import interpret
from interpreter.tokens_ import compiler
from interpreter.util import path

argparser = interpreter.cli.construct_parser()
arguments = argparser.parse_args()

if not arguments.debug:
    sys.tracebacklimit = 0

if arguments.compile == "True":
    compiler_ = (
        compiler.PickleCompiler()
        if arguments.compiled_format == "pickle"
        else compiler.JsonCompiler()
    )
    try:
        tokens = compiler_.read_compiled_file(arguments.filepath)
    except compiler.CompilerError:
        tokens = interpret.construct_tokens(arguments.filepath)
    compiler_.write_compiled_file(tokens, arguments.filepath)
else:
    tokens = interpret.construct_tokens(arguments.filepath)

if arguments.debug:
    for token in tokens:
        interpret.print_token_trace(token)

with path.ChangeDir(folder=os.path.dirname(arguments.filepath)):
    interpret.interpret(tokens, arguments.iterations)
