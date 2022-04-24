# -*- coding: utf-8 -*-
"""Python implementation for the Natscript bitwise library"""

# pylint: disable=redefined-builtin
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import datetime as _datetime
import time as _time


def now():
    return _time.time()


def delay(x):
    _time.sleep(x)


def today(format):
    return _datetime.datetime.now().strftime(format)


__all__ = ["delay", "now", "today"]
