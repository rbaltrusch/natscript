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
        self._current_stack_pop = self._stacks[-1].pop.__call__
        self._current_stack_append = self._stacks[-1].append.__call__
        self._current_variables: Dict[str, Variable] = self._variables[-1]

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
        self._current_stack_pop = self._stacks[-1].pop.__call__
        self._current_stack_append = self._stacks[-1].append.__call__
        self._current_variables = self._variables[-1]

    def remove_stack(self) -> None:
        """Removes the last stack from the stack of stacks"""
        self._stacks.pop()
        self._variables.pop()
        self._current_stack_pop = self._stacks[-1].pop.__call__
        self._current_stack_append = self._stacks[-1].append.__call__
        self._current_variables = self._variables[-1]

    def stack_pop(self) -> Value:
        """Pops and returns the last value on the stack.

        Raises an EmptyStackError if the stack is empty.
        """
        try:
            return self._current_stack_pop()  # pylint: disable=not-callable
        except IndexError:
            raise exceptions.EmptyStackError() from None

    def stack_append(self, value: Value) -> None:
        """Appends the passed Value to the stack"""
        self._current_stack_append(value)  # pylint: disable=not-callable

    def check_variable(self, name: str) -> bool:
        """Returns True if the passed name is in the variables list"""
        return name in self._current_variables

    def get_variable(self, name: str) -> Variable:
        """Returns a Variable if it can be looked up by name.

        Raises an UndefinedVariableException if variable cannot be found.
        """
        try:
            return self._current_variables[name]
        except KeyError:
            raise exceptions.UndefinedVariableException(name) from None

    def set_variable(self, name: str, variable: Variable) -> None:
        """Sets the value of the variable identified by name to the specified variable."""
        self._current_variables[name] = variable

    def remove_variable(self, name: str) -> None:
        """Removes the variable identified by name from the current variable scope"""
        self._current_variables.pop(name)
