"""Provides an extension to use colon to separate filter and its arguments

Jinja uses `{{a | filter(arg)}}`, but liquid uses `{{a | filter: arg}}`
"""
from typing import TYPE_CHECKING, Iterable
from jinja2.ext import Extension
from jinja2.lexer import (
    TOKEN_ASSIGN,
    TOKEN_BLOCK_END,
    TOKEN_COLON,
    TOKEN_LPAREN,
    TOKEN_NAME,
    TOKEN_PIPE,
    TOKEN_RPAREN,
    TOKEN_VARIABLE_END,
    Token,
)

if TYPE_CHECKING:
    from jinja2.lexer import TokenStream


class FilterColonExtension(Extension):
    """This extension allows colon to be used to separate
    the filter and arguments, so that we can write django/liquid-style filters
    """

    def filter_stream(self, stream: "TokenStream") -> Iterable[Token]:
        """Modify the colon to lparen and rparen tokens"""
        # expect a colon
        # 0: don't expect to change any {{a | filter: arg}}
        #    to {{a | filter(arg)}}
        # 1: expect a filter
        # 2: expect the colon
        # 3: expect rparen
        flag = 0

        for token in stream:
            # print(token.value, token.type)
            if flag == 0 and token.type is TOKEN_PIPE:
                flag = 1
                yield token
            elif token.type is TOKEN_NAME and flag == 1:
                flag = 2
                yield token
            elif token.type is TOKEN_COLON and flag == 2:
                flag = 3
                yield Token(token.lineno, TOKEN_LPAREN, None)
            elif token.type is TOKEN_COLON and flag == 3:
                # {{ a | filter: 1, x: 2}} => {{ a | filter: 1, x=2}}
                yield Token(token.lineno, TOKEN_ASSIGN, None)
            elif (
                token.type in (TOKEN_VARIABLE_END, TOKEN_BLOCK_END, TOKEN_PIPE)
                and flag == 3
            ):
                flag = 1 if token.type is TOKEN_PIPE else 0
                yield Token(token.lineno, TOKEN_RPAREN, None)
                yield token
            else:
                yield token
