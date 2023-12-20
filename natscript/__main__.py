# -*- coding: utf-8 -*-
"""
The entry point to the Natscript interpreter.
"""
import os
import sys

import natscript.cli
from natscript import interpret
from natscript.internal import token_
from natscript.tokens_ import compiler
from natscript.util import path

argparser = natscript.cli.construct_parser()
arguments = argparser.parse_args()

if not arguments.debug:
    sys.tracebacklimit = 0

if not arguments.args:
    interpret.run_interactive_shell()

filepath = arguments.args[0]
sys.argv = arguments.args

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
