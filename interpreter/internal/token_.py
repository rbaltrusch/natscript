# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 12:04:45 2021

@author: richa
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, Tuple, Type

from interpreter.internal import exceptions, tokenvalue
from interpreter.internal.interfaces import Interpreter


@dataclass
class TokenFactory:
    """Token and Value factory"""

    tokens: Dict[str, Type[Token]] = field(default_factory=dict)
    regex_tokens: Dict[str, Type[Token]] = field(default_factory=dict)

    def __post_init__(self):
        self._regex_patterns = [(re.compile(k), k) for k in self.regex_tokens]
        self.line_number = 1
        self._value_cache: Dict[Hashable, tokenvalue.Value] = {}
        self._none_value = tokenvalue.NoneValue()

    def create_token(self, token: str) -> Token:
        """Returns a Token matching the specified token string"""
        if token in self.tokens:
            token_type = self.tokens[token]
            return token_type(value=None, line=self.line_number)

        for pattern, key in self._regex_patterns:
            if pattern.search(token):
                token_type = self.regex_tokens[key]
                return token_type(value=token, line=self.line_number)

        raise exceptions.LexError(token, self.line_number) from None

    @staticmethod
    def create_variable(name: str) -> tokenvalue.Variable:
        """Returns a new Variable"""
        return tokenvalue.Variable(name)

    @staticmethod
    def create_constant(variable: tokenvalue.Variable) -> tokenvalue.Constant:
        """Returns a new Constant"""
        return tokenvalue.Constant(variable)

    def create_any_value(self, value: Any) -> tokenvalue.Value:
        """Returns a new Value of the correct Value type.
        This method should be used for values that could be None or iterable.
        """
        if value is None:
            return self.create_none_value()

        try:
            return self.create_value(value)
        except TypeError:
            return self.create_iterable_value(value)

    def create_value(self, value: Hashable) -> tokenvalue.Value:
        """Returns a new Value object if value cannot be found in the value cache,
        otherwise returns the existing Value from the cache.
        """
        return self._value_cache.get(value, tokenvalue.Value(value))

    @staticmethod
    def create_iterable_value(value: Iterable[Any]) -> tokenvalue.IterableValue:
        """Returns a new IterableValue object"""
        return tokenvalue.IterableValue(value)

    def create_none_value(self) -> tokenvalue.NoneValue:
        """Returns the token factory's NoneValue instance"""
        return self._none_value


@dataclass
class ExpectedToken:
    """Class to hold data about expected subtokens for tokens. Relevant to token parsing."""

    types: Tuple[Type[Token], ...]
    run_order: int = 0
    optional: bool = False

    def pop_token_from(self, expected_tokens: List[ExpectedToken]) -> ExpectedToken:
        """Pops the first token from the list."""
        return expected_tokens.pop(0)

    def copy(self) -> ExpectedToken:
        """Returns itself."""
        return self

    @property
    def needs_copy(self) -> bool:
        """Always False"""
        return False


class ExpectedTokenCombination:
    """Class to hold data about combinations of expected subtokens for tokens.
    Relevant to token parsing.
    """

    def __init__(
        self, *tokens: ExpectedToken, optional: bool = False, copied: bool = False
    ):
        self.tokens = list(tokens)
        self.optional = optional
        self.copied = copied

    def pop_token_from(self, expected_tokens: List[ExpectedToken]) -> ExpectedToken:
        """Pops the first token from its own expected tokens list, if it can, otherwise
        from the specified expected_tokens list.
        """
        tokens = self.tokens if self.tokens else expected_tokens
        return tokens.pop(0)

    def copy(self) -> ExpectedTokenCombination:
        """Returns a new ExpectedTokenCombination instance."""
        return self.__class__(*self.tokens, optional=self.optional, copied=True)

    @property
    def needs_copy(self) -> bool:
        """True if token was not copied yet."""
        return not self.copied

    @property
    def types(self) -> Tuple[Type[Token], ...]:
        """The tuple of expected Token types which can be used for typechecking
        using isinstance during token parsing.
        """
        types: List[Type[Token]] = []
        for token in self.tokens:
            types.extend(token.types)
            if not token.optional:
                break
        return tuple(types)

    @property
    def run_order(self) -> int:
        """The run order of the first contained expected token"""
        if not self.tokens:
            return 0
        return self.tokens[0].run_order


class Token:
    """Token class, a composite (can contain any number of nested subtokens)
    that is runnable by the Interpreter.
    """

    EXPECTED_TOKENS: List[ExpectedToken] = []  # type: ignore
    VALUE_FACTORY: Optional[Callable[..., Any]] = None
    TOKEN_FACTORY: TokenFactory = TokenFactory()
    functional = True

    def __init__(self, value: Optional[Any] = None, line: int = 0):
        self.value: Optional[Any] = value
        self.line: int = line
        self.tokens: List[Token] = []
        self.run_order: int = 0
        self.parent: Optional[Token] = None
        self.expected_tokens = self.EXPECTED_TOKENS[:]
        self._sorted_tokens = None
        self.filepath: Optional[str] = None

    def __repr__(self):
        value = "" if self.value is None else f", {self.value}"
        type_ = "Token" if not self.tokens else "SyntaxTree"
        file = "" if not self.filepath else f"File {self.filepath}: "
        return f"{file}Line {self.line}: {type_}({self.__class__.__name__}{value})"

    def init(self, interpreter: Interpreter):
        """Initialises all subtokens, then itself"""
        for token in self.tokens:
            if token.functional:
                interpreter.init(token)  # type: ignore
        self._init(interpreter)

    def _init(self, interpreter: Interpreter):
        """Initialises the token"""

    def run(self, interpreter: Interpreter):
        """Runs all subtokens, then itself"""
        if self._sorted_tokens is None:
            self._sorted_tokens = sorted(
                [x for x in self.tokens if x.functional], key=lambda x: x.run_order
            )

        for token in self._sorted_tokens:
            interpreter.run(token)  # type: ignore
        self._run(interpreter)

    def _run(self, interpreter: Interpreter):
        """Runs the token"""

    def check_optional_token(self, token: Token) -> bool:
        """Returns True if the passed token could syntactically be the next subtoken"""
        all_types = tuple(t for token in self.expected_tokens for t in token.types)
        return isinstance(token, all_types)

    def add_token(self, token: Token):
        """Adds the passed token as a subtoken.
        Raises InternalFullTokenParseError if token is already full.
        """
        if self.full:
            raise exceptions.InternalFullTokenParseError(token) from None  # type: ignore
        self._check_types(token)
        self.tokens.append(token)
        token.parent = self

    def pop_tokens(self, tokens: List[Token]) -> Optional[Token]:
        """Optionally pops any number of tokens from the list"""

    def update_token_factory(self, token_factory: TokenFactory) -> None:
        """Optionally updates the token factory."""

    def raise_syntax_exception(self) -> None:
        """Raises SyntaxException"""
        raise exceptions.SyntaxException(self)  # type: ignore

    def _check_types(self, token: Token):
        while self.expected_tokens:
            if self.expected_tokens[0].needs_copy:
                self.expected_tokens[0] = self.expected_tokens[0].copy()
            expected_token = self.expected_tokens[0].pop_token_from(
                self.expected_tokens
            )
            if isinstance(token, expected_token.types):
                token.run_order = expected_token.run_order
                return

            if not expected_token.optional:
                raise exceptions.ParseTypeError(
                    token, expected_token.types  # type: ignore
                ) from None
        raise exceptions.ParseException(token) from None  # type: ignore

    @property
    def is_subtoken(self) -> bool:
        """Is True if token has a parent"""
        return self.parent is not None

    @property
    def value(self) -> Any:  # type:ignore
        """The value of the token"""
        return self._value

    @value.setter
    def value(self, value: Any) -> None:  # type:ignore
        """Sets the value of token, if possible with its VALUE_FACTORY."""
        if self.VALUE_FACTORY is not None:
            self._value = self.VALUE_FACTORY(value)  # pylint: disable=not-callable
        else:
            self._value: Any = value

    @property
    def full(self) -> bool:
        """True if no expected_tokens are left"""
        return not self.expected_tokens

    @property
    def satisfied(self) -> bool:
        """True if only optional expected tokens are left, if any."""
        mandatory_tokens = [
            token for token in self.expected_tokens if not token.optional
        ]
        return not mandatory_tokens

    @cached_property
    def has_all_optionals(self) -> bool:
        """True if length of tokens matches length of expected tokens"""
        return len(self.tokens) == len(self.EXPECTED_TOKENS)


class ClauseToken(Token):
    """Base class for tokens with a defined start and end token containing any number
    of subtokens.
    """

    CLOSE_TOKEN = Token
    EXPECTED_TOKENS = [ExpectedToken((Token,))] * 1000

    def raise_syntax_exception(self):
        """Raises an UnclosedClauseException"""
        raise exceptions.UnclosedClauseException(self) from None  # type: ignore

    @property
    def full(self) -> bool:
        """True if the token contains a subtoken of its corresponding closing type."""
        return bool(self.tokens) and isinstance(self.tokens[-1], self.CLOSE_TOKEN)  # type: ignore

    @property
    def satisfied(self) -> bool:
        """Returns full status"""
        return self.full


class SkipToken(Token):
    """Base class for tokens that remove themselves from the token list during parsing."""

    def pop_tokens(self, tokens: List[Token]) -> Optional[Token]:
        """Pops the first token from the list"""
        return tokens.pop(0)
