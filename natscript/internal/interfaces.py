# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 13:44:51 2021

@author: richa
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple, Type

# type: ignore
# pylint: disable=duplicate-code


class Token(Protocol):
    """Protocol for executable Tokens"""

    value: Optional[Any]
    line: int
    tokens: List[Token]
    run_order: int
    parent: Optional[Token]
    expected_tokens: List[ExpectedToken]
    filepath: Optional[str]
    functional: bool
    must_be_subtoken: bool

    EXPECTED_TOKENS: List[ExpectedToken]  # type: ignore
    TOKEN_FACTORY: TokenFactory

    def init(self, interpreter: Interpreter) -> None:
        """Initialises the token"""

    def run(self, interpreter: Interpreter) -> None:
        """Runs the token"""

    def check_optional_token(self, token: Token) -> bool:  # type: ignore
        """Returns True if the passed token could syntactically be the next subtoken"""

    def add_token(self, token: Token) -> None:
        """Adds the specified token to its subtokens"""

    def pop_tokens(self, tokens: List[Token]) -> Optional[Token]:
        """Removes any number of tokens from the passed list"""

    def update_token_factory(self, token_factory: TokenFactory) -> None:
        """Updates the token factory"""

    def raise_syntax_exception(self) -> None:
        """Raises SyntaxException"""

    @property
    def is_subtoken(self) -> bool:  # type: ignore
        """Is True if token has a parent"""

    @property
    def full(self) -> bool:  # type: ignore
        """The filling status of the token"""

    @property
    def satisfied(self) -> bool:  # type: ignore
        """True if all mandatory tokens are contained"""

    @property
    def has_all_optionals(self) -> bool:  # type: ignore
        """True if all expected tokens are contained"""


class ExpectedToken(Protocol):
    """Protocol for expected token"""

    types: Tuple[Type[Token], ...]
    run_order: int
    optional: bool

    def pop_token_from(self, expected_tokens: List[ExpectedToken]) -> ExpectedToken:  # type: ignore
        """Pops a token from the list and returns it"""

    def copy(self) -> ExpectedToken:  # type: ignore
        """Returns a copy of the current token"""

    @property
    def needs_copy(self) -> bool:  # type: ignore
        """True if this token needs to be copied (True if mutable)"""


class Value(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for interpreter stack Value objects"""

    value: Any
    inputs: Optional[List[Variable]]

    def get_value(self) -> Any:
        """Returns the actual value of the Value"""

    def convert_to_str(self) -> str:
        """Returns the value of the object as a str"""

    def negate_value(self) -> None:
        """Negates value of Value"""


class NoneValue(Protocol):
    """Protocol class for interpreter NoneValue objects"""

    value: Any
    inputs: Optional[List[Variable]]

    def get_value(self) -> NoneValue:  # type: ignore
        """Returns the actual value of the Value"""


class IterableValue(Protocol):
    """Protocol for interpreter IterableValue objects"""

    value: Iterable[Any]
    inputs: Optional[List[Variable]]

    def get_value(self) -> Iterable[Any]:  # type: ignore
        """Returns the actual value of the Value"""


class Variable(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for interpreter Variable objects"""

    value: Any
    name: str
    inputs: Optional[List[Variable]]

    def get_value(self) -> Any:
        """Returns the actual value of the Variable"""

    def get_qualifier(self, name: str) -> bool:  # type: ignore
        """Returns the value of the queried qualifier"""

    def set_qualifier(self, name: str) -> None:
        """Sets the value of the qualifier to True"""


class TokenFactory(Protocol):
    """Protocol for TokenFactory"""

    tokens: Dict[str, Type[Token]]
    regex_tokens: Dict[str, Type[Token]]
    line_number: int

    def create_token(self, token: str) -> Token:  # type: ignore
        """Returns a new token"""

    @staticmethod
    def create_variable(name: str) -> Variable:  # type: ignore
        """Returns a new Variable"""

    @staticmethod
    def create_constant(variable: Variable) -> Variable:  # type: ignore
        """Returns a new constant Variable"""

    @staticmethod
    def create_value(value: Any) -> Value:  # type: ignore
        """Returns a new Value"""

    def create_any_value(self, value: Any) -> Value:  # type: ignore
        """Returns a new value of the correct type"""

    @staticmethod
    def create_iterable_value(value: Iterable[Any]) -> IterableValue:  # type: ignore
        """Creates a new iterable value"""

    def create_none_value(self) -> NoneValue:  # type: ignore
        """Creates a new NoneValue"""


class Interpreter(Protocol):
    """Protocol for token interpreter"""

    def run(self, token: Token) -> None:
        """Runs the token"""

    def init(self, token: Token) -> None:
        """Runs the token"""

    def add_stack(self) -> None:
        """Adds a new stack"""

    def remove_stack(self) -> None:
        """Removes the last stack"""

    def stack_pop(self) -> Value:  # type: ignore
        """Pops the last value from the current stack"""

    def stack_append(self, value: Value) -> None:
        """Appends a value to the current stack"""

    def check_variable(self, name: str) -> bool:  # type: ignore
        """Checks whether the specified name identifies a declared variable"""

    def get_variable(self, name: str) -> Variable:  # type: ignore
        """Returns the value of the variable specified by name"""

    def set_variable(self, name: str, variable: Variable) -> None:
        """Saves the variable specified by name and the corresponding Variable object"""

    def remove_variable(self, name: str) -> None:
        """Removes the variable identified by name from the current variable scope"""


class TokenCompiler(Protocol):
    """Protocol for token compiler"""

    exception: Type[Exception]

    def write_compiled_file(self, tokens_: List[Token], filename: str) -> None:
        """Traverses all token trees to collect their data, then dumps token data to file"""

    def read_compiled_file(self, filename: str) -> List[Token]:
        """Loads tokens from the corresponding compiled file to the filename specified."""
