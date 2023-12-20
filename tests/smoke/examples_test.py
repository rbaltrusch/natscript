# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:40:44 2021

@author: richa
"""

import glob
import os

from interpreter import interpret
from interpreter.tokens_ import compiler


def test_examples():
    _delete_compiled_files()
    _run_test_()  # without compiled files
    _run_test_()  # with compiled files


def _delete_compiled_files():
    compiled_filepaths = glob.glob("../doc/examples/**/*.natc", recursive=True)
    for filepath in compiled_filepaths:
        os.unlink(filepath)


def _run_test_():
    filepaths = glob.glob("../doc/examples/**/*.nat", recursive=True)
    original_dir = os.getcwd()
    compiler_ = compiler.PickleCompiler()
    for filepath in filepaths:
        print(f"Running {filepath}...")

        os.chdir(os.path.dirname(filepath))
        filename = os.path.basename(filepath)

        try:
            try:
                tokens = compiler_.read_compiled_file(filename)
            except compiler.CompilerError:
                tokens = interpret.construct_tokens(filename)

            compiler_.write_compiled_file(tokens, filename)
            interpret.interpret(tokens)
            passed = True
        except Exception as exc:
            raise exc
        assert passed, f"{filepath} could not be interpreted!"

        os.chdir(original_dir)
        print(f"{filepath} passed.")
