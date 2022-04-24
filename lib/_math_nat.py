# -*- coding: utf-8 -*-
"""Python implementation for the Natscript math library"""

from math import ceil as _ceil
from math import floor as _floor
from math import prod as _prod
from operator import mod as _mod
from operator import pow as _pow

# pylint: disable=redefined-builtin
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

_sum = sum
_abs = abs
_min = min
_max = max
_round = round


def modulus(x, y):
    return _mod(x, y)


def exponentiate(x, y):
    return _pow(x, y)


def product(x):
    return _prod(x)


def ceil(x):
    return _ceil(x)


def floor(x):
    return _floor(x)


def sum(x):
    return _sum(x)


def absolute(x):
    return _abs(x)


def minimum(x):
    return _min(x)


def maximum(x):
    return _max(x)


def round(x):
    return _round(x)


__all__ = [
    "absolute",
    "minimum",
    "maximum",
    "round",
    "floor",
    "ceil",
    "sum",
    "product",
    "modulus",
    "exponentiate",
]
