# -*- coding: utf-8 -*-
"""Python implementation for the Natscript string library"""

from string import ascii_lowercase as alphabet

# pylint: disable=missing-docstring
# pylint: disable=invalid-name


def lower(x: str):
    return x.lower()


def upper(x: str):
    return x.upper()


def split(x: str, delimiter=None):
    return x.split() if delimiter is None else x.split(delimiter)


def join(x: str, delimiter=None):
    return "".join(x) if delimiter is None else delimiter.join(x)


def trim(x: str):
    return x.strip()


def replace(x: str, old, new):
    return x.replace(old, new)


__all__ = ["lower", "upper", "split", "join", "trim", "replace", "alphabet"]
