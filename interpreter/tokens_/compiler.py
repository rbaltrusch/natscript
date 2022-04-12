# -*- coding: utf-8 -*-
"""
This module contains the bytecode compiler for the Natscript interpreter.

Public interface:
    read_compiled_file
    write_compiled_file
    get_compiled_filename

"""

import os
import pickle
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Type

from tokens_ import tokens
from interpreter.token_ import Token


TokenData = Tuple[int, str, Any, int, int, int]


class CompilerError(Exception):
    """CompilerError exception, gets thrown when the compiled file
    for a corresponding source code file cannot be read or is not current.
    """


def _hash_file(filename: str) -> str:
    """Returns the hash of the contents of the specified file."""
    hash_ = hashlib.sha256()
    bytes_ = bytearray(128 * 1024)
    memory_view = memoryview(bytes_)
    with open(filename, "rb", buffering=0) as file:
        for n in iter(lambda: file.readinto(memory_view), 0):
            hash_.update(memory_view[:n])
    return hash_.hexdigest()


def get_compiled_filename(filename: str) -> str:
    """Gets the name of the compiled file corresponding to the specified source code filename."""
    return filename.replace(".nat", ".natc")


def write_compiled_file(tokens: List[Token], filename: str) -> None:
    """Traverses all token trees to collect their data, then dumps token data
    to pickle file, along with a current filehash of the source code file specified.
    """
    saved_tokens = []
    for token in tokens:
        _save_tokens(token, saved_tokens)

    content = {"tokens": saved_tokens, "hash": _hash_file(filename)}
    compiled_filename = get_compiled_filename(filename)
    with open(compiled_filename, "wb") as file:
        pickle.dump(content, file)


def _save_tokens(
    token: Token, list_: List[TokenData], id_: int = 0, parent_id: Optional[int] = None
) -> None:
    """Recursively traverses token and its subtokens and appends their token data to the list."""
    list_.append(
        (
            id_,
            token.__class__.__name__,
            token.value,
            token.run_order,
            parent_id,
            token.line,
        )
    )
    for token in token.tokens:
        _save_tokens(token, list_, id_ + 1, parent_id=id_)


def read_compiled_file(filename: str) -> List[Token]:
    """Loads tokens from the corresponding compiled file to the filename specified.

    If a compiled file cannot be found or the file hash of the source code file and
    the hash in the compiled file do not match, a CompilerError exception is thrown.
    """
    compiled_filename = get_compiled_filename(filename)
    if not os.path.isfile(compiled_filename):
        raise CompilerError("Compiled file does not exist!")

    with open(compiled_filename, "rb") as file:
        contents = pickle.load(file)

    if _hash_file(filename) != contents["hash"]:
        raise CompilerError("Hash in compiled file did not match file hash!")

    tokens_ = _construct_token_trees(token_data=contents["tokens"])
    return tokens_


def _construct_token_trees(token_data: List[TokenData]) -> List[Token]:
    """Constructs a list of nested token trees from the passed token data."""
    parents: Dict[str, Token] = {}
    tokens_ = []
    expected_tokens = []
    for id_, class_name, value, run_order, parent_id, line in token_data:
        class_: Type[Token] = tokens.__dict__[class_name]
        token_ = class_(value, line)
        token_.run_order = run_order
        token_.expected_tokens = expected_tokens

        parents[id_] = token_
        if parent_id is None:
            tokens_.append(token_)
        else:
            parents[parent_id].tokens.append(token_)
    return tokens_
