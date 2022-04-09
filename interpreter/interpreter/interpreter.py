# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""
from typing import Any
from typing import Dict
from typing import List

from interpreter import exceptions
from interpreter.interfaces import Token
from interpreter.interfaces import Value
from interpreter.interfaces import Variable

class Interpreter:
    """Interprets tokens and keeps track of the program state"""

    def __init__(self):
        self._stacks: List[List[Value]] = [[]]
        self._variables: List[Dict[str, Variable]] = [{}]

    def interpret(self, token: Token) -> None:
        """Runs the current token"""
        try:
            if not token.satisfied:
                raise exceptions.SyntaxException(token)
            token.run(self)
        except exceptions.RunTimeException as e:
            e.line = token.line
            raise e

    def add_stack(self) -> None:
        """Adds a stack to the stack of stacks"""
        self._stacks.append([])
        self._variables.append({})

    def remove_stack(self) -> None:
        """Removes the last stack from the stack of stacks"""
        self._stacks.pop()
        self._variables.pop()

    def stack_pop(self) -> Value:
        """Pops and returns the last value on the stack.

        Raises an InternalEmptyStackError if the stack is empty.
        """
        if not self._stacks or not self._stacks[-1]:
            raise exceptions.InternalEmptyStackError()
        return self._stacks[-1].pop()

    def stack_append(self, value: Value) -> None:
        """Appends the passed Value to the stack"""
        self._stacks[-1].append(value)

    def check_variable(self, name: str) -> bool:
        """Returns True if the passed name is in the variables list"""
        return name in self._variables[-1]

    def get_variable(self, name: str) -> Variable:
        """Returns a Variable if it can be looked up by name.

        Raises an UndefinedVariableException if variable cannot be found.
        """

        try:
            value = self._variables[-1][name]
        except KeyError:
            #pylint: disable=raise-missing-from
            raise exceptions.UndefinedVariableException(name)
        return value

    def set_variable(self, name: str, value: Any) -> None:
        """Sets the value of the variable identified by name to the specified value."""
        self._variables[-1][name] = value
