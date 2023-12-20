# -*- coding: utf-8 -*-
"""Python implementation for the Natscript regex library"""

# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import re as _re


def find(string, pattern):
    return _re.findall(pattern, string)


def replace(string, pattern, new):
    return _re.sub(pattern, new, string)


__all__ = ["find", "replace"]
