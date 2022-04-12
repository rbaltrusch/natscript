# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:17:11 2020

@author: Korean_Crimson
"""
from typing import Dict
from typing import List

import internal.exceptions as exceptions
from internal.interfaces import Token
from internal.interfaces import Value
from internal.interfaces import Variable

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
            token.print_token_stack()
            e.line = token.TOKEN_STACK[-1].line
            raise e
        except Exception as e:
            token.print_token_stack()
            raise e

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
            return self._variables[-1][name]
        except KeyError:
            raise exceptions.UndefinedVariableException(name)

    def set_variable(self, name: str, variable: Variable) -> None:
        """Sets the value of the variable identified by name to the specified variable."""
        self._variables[-1][name] = variable

    def remove_variable(self, name: str) -> None:
        """Removes the variable identified by name from the current variable scope"""
        self._variables[-1].pop(name)
