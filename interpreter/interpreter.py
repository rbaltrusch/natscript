# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

import exceptions

class Interpreter:
    def __init__(self):
        self._stack = []
        self._variables = {}

    def interpret(self, block):
        block.run(self)

    def stack_pop(self):
        if not self._stack:
            raise exceptions.InternalEmptyStackError()
        return self._stack.pop()

    def stack_append(self, value):
        self._stack.append(value)

    def check_variable(self, name):
        return name in self._variables

    def get_variable(self, name):
        try:
            value = self._variables[name]
        except KeyError:
            raise exceptions.UndefinedVariableException(name)
        return value

    def set_variable(self, name, value):
        self._variables[name] = value
