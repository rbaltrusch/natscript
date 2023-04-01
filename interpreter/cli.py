# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 13:54:26 2022

@author: Korean_Crimson
"""
import argparse


def construct_parser() -> argparse.ArgumentParser:
    """Returns the cli argument parser"""
    parser = argparse.ArgumentParser(
        "interpreter",
        description="CLI for the Natscript interpreter",
        allow_abbrev=True,
    )

    parser.add_argument(
        "filepath",
        help="The path of the Natscript file to be run",
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enables the interpreter debug mode"
    )

    parser.add_argument(
        "--compile", "-c", nargs=1, default="True", help="Enables the bytecode compiler"
    )

    parser.add_argument(
        "--compiled-format",
        "-f",
        choices=["pickle", "json"],
        default="pickle",
        help="Specifies the format of the bytecode-compiled file",
    )
    parser.add_argument(
        "--iterations",
        "-i",
        default=1,
        type=int,
        help="Specifies how often the script should be executed",
    )
    return parser
