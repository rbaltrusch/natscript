# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

from typing import List, Dict, Any

import exceptions
from interfaces import Value, Variable

class Interpreter:
    def __init__(self):
        self._stack: List[Value] = []
        self._variables: Dict[str, Variable] = {}

    def interpret(self, block) -> None:
        block.run(self)

    def stack_pop(self) -> Value:
        if not self._stack:
            raise exceptions.InternalEmptyStackError()
        return self._stack.pop()

    def stack_append(self, value: Value) -> None:
        self._stack.append(value)

    def check_variable(self, name: str) -> bool:
        return name in self._variables

    def get_variable(self, name: str) -> Variable:
        try:
            value = self._variables[name]
        except KeyError:
            raise exceptions.UndefinedVariableException(name)
        return value

    def set_variable(self, name: str, value: Any) -> None:
        self._variables[name] = value
