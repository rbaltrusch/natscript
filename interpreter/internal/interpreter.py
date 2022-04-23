# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""
from typing import Dict, List

from interpreter.internal import exceptions
from interpreter.internal.interfaces import Value, Variable

# Cant use Token interface because of bugged typechecking for reassigned class variables
from interpreter.internal.token_ import Token


class Interpreter:
    """Interprets tokens and keeps track of the program state"""

    def __init__(self):
        self._stacks: List[List[Value]] = [[]]
        self._variables: List[Dict[str, Variable]] = [{}]

    def run(self, token: Token) -> None:
        """Runs the current token"""
        try:
            token.run(self)  # type: ignore
        except exceptions.RunTimeException as exc:
            exc.token_stack.append(token)  # type: ignore
            raise exc

    def init(self, token: Token) -> None:
        """Initialises the current token"""
        try:
            if not token.satisfied:
                token.raise_syntax_exception()
            token.init(self)  # type: ignore
        except exceptions.RunTimeException as exc:
            exc.token_stack.append(token)  # type: ignore
            raise exc

    def add_stack(self) -> None:
        """Adds a stack to the stack of stacks"""
        self._stacks.append([])
        globals_dict = self._variables[0].copy()
        self._variables.append(globals_dict)

    def remove_stack(self) -> None:
        """Removes the last stack from the stack of stacks"""
        self._stacks.pop()
        self._variables.pop()

    def stack_pop(self) -> Value:
        """Pops and returns the last value on the stack.

        Raises an EmptyStackError if the stack is empty.
        """
        try:
            return self._stacks[-1].pop()
        except IndexError:
            raise exceptions.EmptyStackError() from None

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
            return self._variables[-1][name]
        except KeyError:
            raise exceptions.UndefinedVariableException(name) from None

    def set_variable(self, name: str, variable: Variable) -> None:
        """Sets the value of the variable identified by name to the specified variable."""
        self._variables[-1][name] = variable

    def remove_variable(self, name: str) -> None:
        """Removes the variable identified by name from the current variable scope"""
        self._variables[-1].pop(name)
