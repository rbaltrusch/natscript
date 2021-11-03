# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 23:00:03 2021

@author: richa
"""

class ParseTypeError(Exception):
    def __init__(self, token, types):
        super().__init__(f'Expected {types=}, but got {token}!')

class EmptyStackError(Exception):
    def __init__(self):
        self.message = 'Could not pop value from empty stack!'
        super().__init__(self.message)
