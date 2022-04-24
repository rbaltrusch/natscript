# -*- coding: utf-8 -*-
"""Python implementation for the Natscript bitwise library"""

# pylint: disable=missing-docstring
# pylint: disable=invalid-name


def bitwise_and(x, y):
    return x & y


def bitwise_or(x, y):
    return x | y


def bitwise_xor(x, y):
    return x ^ y


def bitwise_not(x):
    return ~x


def bitshift_left(x, y):
    return x << y


def bitshift_right(x, y):
    return x >> y


__all__ = [
    "bitwise_and",
    "bitwise_or",
    "bitwise_xor",
    "bitwise_not",
    "bitshift_left",
    "bitshift_right",
]
