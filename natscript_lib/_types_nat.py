# -*- coding: utf-8 -*-
"""Python implementation for the Natscript types library"""

# pylint: disable=redefined-builtin
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring
_float = float
_list = list


def string(x):
    return str(x)


def integer(x):
    return int(x)


def number(x):
    if x == int(x):
        return int(x)
    return float(x)


def float(x):
    return _float(x)


def list(x):
    return _list(x)


def binary(x):
    return bin(x)


def hexadecimal(x):
    return hex(x)


__all__ = ["string", "integer", "number", "float", "list", "binary", "hexadecimal"]
