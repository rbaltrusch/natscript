# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, DefaultDict, List

from interpreter.internal import exceptions


@dataclass
class Value:
    """Base Value class for values on the interpreter stack"""

    value: Any = None
    source: Any = None

    def __post_init__(self):
        self.inputs = None

    def get_value(self):
        """Returns its value"""
        return self.value

    def negate_value(self) -> None:
        """Negates its value"""
        self.value = not self.value

    def __repr__(self):
        if isinstance(self.value, bool):
            return str(self.value).lower()
        if callable(self.value):
            return f"function {self.value.__name__}"
        return str(self.value)

    def convert_to_str(self) -> str:
        """Converts the value of the object to str"""
        return self.__repr__()


class IterableValue(Value):
    """Value wrapper for lists"""

    def get_value(self) -> List[Any]:
        """Returns a list of actual values contained in the list.
        Converts any contained Value objects into their respective value.
        """
        if isinstance(self.value, dict):
            return {k: self._get_item(v) for k, v in self.value.items()}
        return [self._get_item(x) for x in self.value]

    @staticmethod
    def _get_item(value: Value):
        try:
            return value.get_value()
        except AttributeError:
            return value


class NoneValue(Value):
    """Value wrapper for None"""

    def __str__(self):
        return "nothing"

    def convert_to_str(self) -> str:
        return "nothing"

    def get_value(self):
        """Returns itself. Cannot return None because this would cause problems
        for Variable objects thinking they are undefined."""
        return self


class Variable(Value):
    """Variable class for variables living in interpreter variable scopes"""

    def __init__(self, name: str):  # pylint: disable=super-init-not-called
        self.name = name
        self.inputs = None
        self.source = None
        self.qualifiers: DefaultDict[str, bool] = defaultdict(bool)

    def convert_to_str(self) -> str:
        self.get_value()
        return super().__repr__()

    def get_value(self) -> Any:
        """Returns its value. If it's None, it raises an UndefinedVariableException"""
        if self.value is None:
            raise exceptions.UndefinedVariableException(self.name)
        return self.value

    def add_qualifier(self, qualifier: str) -> None:
        """Sets the qualifier specified by name to True"""
        self.qualifiers[qualifier] = True

    def get_qualifier(self, qualifier: str) -> bool:
        """Returns the value of the specified qualifier"""
        return self.qualifiers[qualifier]


class Constant(Variable):
    """Variable with a value that cannot be changed once set"""

    def __init__(self, variable: Variable):
        self._value = variable.value
        super().__init__(variable.name)

    @property
    def value(self):
        """The value of the Constant"""
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Sets the value of the constant and throws a RunTimeException if it was already set."""
        if self._value is not None:
            raise exceptions.RunTimeException("Cannot assign new value to a constant!")
        self._value = value
