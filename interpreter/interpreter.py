# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

class InterpreterError(Exception):
    def __init__(self, block):
        self.message = f'The following block had no type to be interpreted: {block}!'
        super().__init__(self.message)

class EmptyStackError(Exception):
    def __init__(self):
        self.message = 'Could not pop value from empty stack!'
        super().__init__(self.message)

class Interpreter:
    def __init__(self):
        self.stack = []
        self.variables = {}

    def interpret(self, block):
        block.run(self)

    def pop(self):
        if not self.stack:
            raise EmptyStackError()

        value = self.stack.pop()
        return self.variables.get(value, value)
