"""Provides an extension to implment features for standard liquid"""

from typing import TYPE_CHECKING, Generator
from jinja2.lexer import (
    TOKEN_ADD,
    TOKEN_COMMA,
    TOKEN_INTEGER,
    TOKEN_LPAREN,
    TOKEN_NAME,
    TOKEN_RPAREN,
    TOKEN_DOT,
    Token,
)

from ..utils import peek_tokens
from ..tags.standard import standard_tags

from .ext import LiquidExtension

if TYPE_CHECKING:
    from jinja2.lexer import TokenStream


class LiquidStandardExtension(LiquidExtension):
    """This extension implement features for standard liqiud

    These features (that jinja does support) including
    1. Allow '.size' to get length of an array (by replacing it
        with '.__len__()')
    2. Allow 'contains' to work as an operator by turning it into a test
    3. Turn 'forloop' to 'loop'
    4. Allow `(1..5)`, which will be turned to `range(1, 6)`
    """

    tag_manager = standard_tags

    def __init__(self, environment):
        super().__init__(environment)
        environment.tests["contains"] = lambda cont, elm: cont.__contains__(
            elm
        )

    def filter_stream(self, stream: "TokenStream") -> Generator:
        """Supports for liquid features"""
        for token in stream:
            # .size => .__len__()
            if token.type is TOKEN_DOT:

                if stream.current.test("name:size"):
                    stream.skip()  # skip 'size'
                    yield token
                    yield Token(token.lineno, "name", "__len__")
                    yield Token(token.lineno, "lparen", None)
                    yield Token(token.lineno, "rparen", None)
                else:
                    yield token

            # turn "contains" to "is contains" to use "contains" as a test
            elif token.test("name:contains"):
                yield Token(token.lineno, "name", "is")
                yield token

            # turn forloop to loop
            elif token.test("name:forloop"):
                # only when we do forloop.xxx
                if stream.current.type is TOKEN_DOT:
                    yield Token(token.lineno, "name", "loop")
                else:
                    yield token

            # (a..b) => range(a, b + 1)
            elif token.type is TOKEN_LPAREN and stream.current.type in (
                TOKEN_NAME,
                TOKEN_INTEGER,
            ):
                tokens_ahead = peek_tokens(stream, 5)
                # print(tokens_ahead)
                if (
                    len(tokens_ahead) < 5
                    or tokens_ahead[0].type not in (TOKEN_INTEGER, TOKEN_NAME)
                    or tokens_ahead[1].type is not TOKEN_DOT
                    or tokens_ahead[2].type is not TOKEN_DOT
                    or tokens_ahead[3].type not in (TOKEN_INTEGER, TOKEN_NAME)
                    or tokens_ahead[4].type is not TOKEN_RPAREN
                ):
                    yield token
                else:
                    stream.skip(5)
                    yield Token(token.lineno, TOKEN_NAME, "range")
                    yield Token(token.lineno, TOKEN_LPAREN, None)
                    yield tokens_ahead[0]
                    yield Token(token.lineno, TOKEN_COMMA, None)
                    yield tokens_ahead[3]
                    yield Token(token.lineno, TOKEN_ADD, None)
                    yield Token(token.lineno, TOKEN_INTEGER, 1)  # type: ignore
                    yield Token(token.lineno, TOKEN_RPAREN, None)

            else:
                yield token
