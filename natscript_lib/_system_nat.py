# -*- coding: utf-8 -*-
"""Python implementation for the Natscript system library"""

# pylint: disable=redefined-builtin
# pylint: disable=missing-docstring
# pylint: disable=invalid-name

import os as _os
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys


def join_path(paths):
    return _os.path.join(*paths)


def list(path):
    return _os.listdir(path)


def make_folder(path):
    return _os.makedirs(path)


def is_folder(path):
    return _os.path.isdir(path)


def is_file(path):
    return _os.path.isfile(path)


def change_directory(path):
    return _os.chdir(path)


def delete_folder(path):
    _shutil.rmtree(path)


def delete_file(path):
    _os.unlink(path)


def move_folder(source, destination):
    return _shutil.move(source, destination)


def move_file(source, destination):
    _os.rename(source, destination)


def copy_file(source, destination):
    return _shutil.copyfile(source, destination)


def copy_folder(source, destination):
    return _shutil.copy(source, destination)


def system_call(
    args, shell=False, timeout=None  # pylint: disable=redefined-outer-name
):
    return _subprocess.check_call(args, timeout=timeout, shell=shell)


def get_env(variable):
    return _os.getenv(variable)


args = _sys.argv
path = _sys.path

__all__ = [
    "join_path",
    "list",
    "make_folder",
    "is_folder",
    "is_file",
    "change_directory",
    "delete_folder",
    "delete_file",
    "copy_file",
    "copy_folder",
    "move_file",
    "move_folder",
    "system_call",
    "get_env",
    "args",
    "path",
]
