# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:40:44 2021

@author: richa
"""

import glob

from interpret import interpret

def test_examples():
    filepaths = glob.glob('../examples/**/*.nat', recursive=True)
    for filepath in filepaths:
        print(f'Running {filepath}...')
        with open(filepath, 'r') as file:
            file_contents = file.read()

        try:
            interpret(file_contents)
            passed = True
        except Exception as exc:
            raise exc
        assert passed, f'{filepath} could not be interpreted!'
        print(f'{filepath} passed.')
