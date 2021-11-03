# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

import internal

class Interpreter:
    def __init__(self):
        self.stack = []
        self.variables = {}

    def interpret(self, block):
        block.run(self)

    def stack_pop(self):
        if not self.stack:
            raise internal.EmptyStackError()

        value = self.stack.pop()
        return self.variables.get(value, value)
