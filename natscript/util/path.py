# -*- coding: utf-8 -*-
"""Module containing path utils"""
import os


class ChangeDir:
    """Context manager that temporarily changes directory to a folder"""

    def __init__(self, folder):
        self.original_dir = os.getcwd()
        self.folder = os.path.abspath(folder)

    def __enter__(self):
        os.chdir(self.folder)
        return self

    def __exit__(self, *_):
        os.chdir(self.original_dir)
