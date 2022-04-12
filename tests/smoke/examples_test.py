# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:40:44 2021

@author: richa
"""

import glob

import interpret

def test_examples():
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
