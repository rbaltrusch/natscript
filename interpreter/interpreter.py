# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

import internal
import exceptions

class Interpreter:
    def __init__(self):
        self._stack = []
        self._variables = {}

    def interpret(self, block):
        block.run(self)

    def stack_pop(self):
        if not self._stack:
            raise internal.EmptyStackError()
        return self._stack.pop()

    def stack_append(self, value):
        self._stack.append(value)

    def check_variable(self, name):
        return name in self._variables

    def get_variable(self, name):
        try:
            value = self._variables[name]
        except KeyError as e:
            raise exceptions.UndefinedVariableException(name) from e
        return value

    def set_variable(self, variable, value):
        self._variables[variable] = value
