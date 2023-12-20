# -*- coding: utf-8 -*-
"""Python implementation for the Natscript json library"""

# pylint: disable=redefined-builtin
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import json as _json


def jsonwrite(object, filename, encoding="utf-8", indent=4, **kwargs):
    with open(filename, "w", encoding=encoding) as file:
        _json.dump(object, file, indent=indent, **kwargs)


def jsonread(filename, encoding="utf-8"):
    with open(filename, "r", encoding=encoding) as file:
        return _json.load(file)


__all__ = ["jsonwrite", "jsonread"]
