# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 21:51:28 2021

@author: richa
"""
from dataclasses import dataclass
from typing import Any

from internal import exceptions


@dataclass
class Value:
    value: Any = None
    source: Any = None

    def __post_init__(self):
        self.inputs = None

    def get_value(self):
        if self.value is None:
            raise exceptions.UndefinedVariableException(self)
        return self.value

    def negate_value(self) -> None:
        self.value = not self.value

    def __repr__(self):
        if isinstance(self.value, bool):
            return str(self.value).lower()
        return str(self.value)


class IterableValue(Value):
    def get_value(self):
        values = []
        for value in self.value:
            try:
                value: Value
                val = value.get_value()
            except AttributeError:
                val = value
            values.append(val)
        return values


class NoneValue(Value):
    def __repr__(self):
        return "none"

    def get_value(self):
        return self


class Variable(Value):
    def __init__(self, name: str): # pylint: disable=super-init-not-called
        self.name = name
        self.inputs = []
        self.source = None

    def __repr__(self):
        return f'{self.name}'
