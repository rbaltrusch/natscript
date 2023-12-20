# -*- coding: utf-8 -*-
"""
This module contains the bytecode compiler for the Natscript interpreter.

Public interface:

    JsonCompiler/PickleCompiler:
        read_compiled_file
        write_compiled_file
        get_compiled_filename

"""
import abc
import hashlib
import json
import os
import pickle
import re
from typing import Any, Dict, List, Optional, Tuple, Type

from natscript.internal.token_ import Token  # type: ignore
from natscript.tokens_ import tokens

TokenData = Tuple[int, str, Any, int, Optional[int], int]


class CompilerError(Exception):
    """CompilerError exception, gets thrown when the compiled file
    for a corresponding source code file cannot be read or is not current.
    """


class BytecodeCompiler(abc.ABC):
    """Bytecode compiler class, stores token data to bypass lexing and parsing"""

    exception = CompilerError

    def write_compiled_file(self, tokens_: List[Token], filename: str) -> None:
        """Traverses all token trees to collect their data, then dumps token data
        to pickle file, along with a current filehash of the source code file specified.
        """
        saved_tokens: List[TokenData] = []
        for token in tokens_:
            _save_tokens(token, saved_tokens)

        content = {"tokens": saved_tokens, "hash": _hash_file(filename)}
        compiled_filename = self.get_compiled_filename(filename)
        self.write_content_to_file(content, compiled_filename)

    def read_compiled_file(self, filename: str) -> List[Token]:
        """Loads tokens from the corresponding compiled file to the filename specified.

        If a compiled file cannot be found or the file hash of the source code file and
        the hash in the compiled file do not match, a CompilerError exception is thrown.
        """
        compiled_filename = self.get_compiled_filename(filename)
        if not os.path.isfile(compiled_filename):
            raise CompilerError("Compiled file does not exist!")

        contents = self.read_content_from_file(compiled_filename)
        if _hash_file(filename) != contents["hash"]:
            raise CompilerError("Hash in compiled file did not match file hash!")

        tokens_ = _construct_token_trees(token_data=contents["tokens"])
        return tokens_

    @abc.abstractmethod
    def get_compiled_filename(self, filename: str) -> str:
        """Returns the name of the compiled file corresponding to the specified filename"""

    @abc.abstractmethod
    def write_content_to_file(self, content: Any, compiled_filename: str) -> None:
        """Writes the content to the compiled file"""

    @abc.abstractmethod
    def read_content_from_file(self, compiled_filename: str) -> Dict[str, Any]:
        """Reads the content from the compiled file"""


class PickleCompiler(BytecodeCompiler):
    """Bytecode compiler using pickle to write/read compiled files"""

    def write_content_to_file(self, content: Any, compiled_filename: str) -> None:
        """Writes the content to the compiled file"""
        with open(compiled_filename, "wb") as file:
            pickle.dump(content, file)

    def read_content_from_file(self, compiled_filename: str) -> Dict[str, Any]:
        """Reads the content from the compiled file"""
        with open(compiled_filename, "rb") as file:
            contents = pickle.load(file)
        return contents

    def get_compiled_filename(self, filename: str) -> str:
        """Returns the name of the compiled file corresponding to the specified filename"""
        _, ext = os.path.splitext(filename)
        return re.sub(rf"{ext}$", ".natc", filename)


class JsonCompiler(BytecodeCompiler):
    """Bytecode compiler using json to write/read compiled files"""

    def write_content_to_file(self, content: Any, compiled_filename: str) -> None:
        """Writes the content to the compiled file"""
        with open(compiled_filename, "w", encoding="utf-8") as file:
            json.dump(content, file)

    def read_content_from_file(self, compiled_filename: str) -> Dict[str, Any]:
        """Reads the content from the compiled file"""
        with open(compiled_filename, "r", encoding="utf-8") as file:
            contents = json.load(file)
        return contents

    def get_compiled_filename(self, filename: str) -> str:
        """Returns the name of the compiled file corresponding to the specified filename"""
        _, ext = os.path.splitext(filename)
        return re.sub(rf"{ext}$", ".json", filename)


def _hash_file(filename: str) -> str:
    """Returns the hash of the contents of the specified file."""
    hash_ = hashlib.sha256()
    bytes_ = bytearray(128 * 1024)
    memory_view = memoryview(bytes_)
    with open(filename, "rb", buffering=0) as file:
        for n in iter(lambda: file.readinto(memory_view), 0):  # type: ignore
            hash_.update(memory_view[:n])
    return hash_.hexdigest()


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


def _construct_token_trees(token_data: List[TokenData]) -> List[Token]:
    """Constructs a list of nested token trees from the passed token data."""
    parents: Dict[int, Token] = {}
    tokens_: List[Token] = []
    expected_tokens = []  # type: ignore
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
