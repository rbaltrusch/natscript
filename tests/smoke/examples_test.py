# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:40:44 2021

@author: richa
"""

import os
import glob

import interpret

def test_examples():
    _delete_compiled_files()
    _run_test_() #without compiled files
    _run_test_() #with compiled files

def _delete_compiled_files():
    compiled_filepaths = glob.glob('../examples/**/*.natc', recursive=True)
    for filepath in compiled_filepaths:
        os.unlink(filepath)

def _run_test_():
    filepaths = glob.glob('../examples/**/*.nat', recursive=True)
    for filepath in filepaths:
        print(f'Running {filepath}...')

        try:
            interpret.interpret(filepath)
            passed = True
        except Exception as exc:
            raise exc
        assert passed, f'{filepath} could not be interpreted!'
        print(f'{filepath} passed.')
