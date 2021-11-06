# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""

from typing import List, Dict, Any

import exceptions
from interfaces import Value, Variable, Block

class Interpreter:
    """Interprets blocks and keeps track of the program state"""

    def __init__(self):
        self._stack: List[Value] = []
        self._variables: Dict[str, Variable] = {}

    def interpret(self, block: Block) -> None:
        """Runs the current block"""
        block.run(self)

    def stack_pop(self) -> Value:
        """Pops and returns the last value on the stack.

        Raises an InternalEmptyStackError if the stack is empty.
        """
        if not self._stack:
            raise exceptions.InternalEmptyStackError()
        return self._stack.pop()

    def stack_append(self, value: Value) -> None:
        """Appends the passed Value to the stack"""
        self._stack.append(value)

    def check_variable(self, name: str) -> bool:
        """Returns True if the passed name is in the variables list"""
        return name in self._variables

    def get_variable(self, name: str) -> Variable:
        """Returns a Variable if it can be looked up by name.

        Raises an UndefinedVariableException if variable cannot be found.
        """

        try:
            value = self._variables[name]
        except KeyError:
            #pylint: disable=raise-missing-from
            raise exceptions.UndefinedVariableException(name)
        return value

    def set_variable(self, name: str, value: Any) -> None:
        """Sets the value of the variable identified by name to the specified value."""
        self._variables[name] = value
