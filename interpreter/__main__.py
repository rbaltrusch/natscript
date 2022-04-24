# -*- coding: utf-8 -*-
"""
The entry point to the Natscript interpreter.
"""
import os
import sys

import interpreter.cli
from interpreter import interpret
from interpreter.tokens_ import compiler

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

original_dir = os.getcwd()
os.chdir(os.path.abspath(os.path.dirname(arguments.filepath)))
try:
    interpret.interpret(tokens, arguments.iterations)
finally:
    os.chdir(original_dir)
