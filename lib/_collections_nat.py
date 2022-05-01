# -*- coding: utf-8 -*-
"""Python implementation for the Natscript collections library"""

from collections import Counter as _Counter

# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring


def count(x):
    return _Counter(x)


def hashmap(x=None):
    if x is None:
        return {}
    return dict(x)


__all__ = ["count", "hashmap"]
