"""Some utils"""
from os import PathLike
from typing import TYPE_CHECKING, Iterable, List, Union
from jinja2 import nodes
from jinja2.lexer import TOKEN_INTEGER, TOKEN_NAME
from jinja2.exceptions import TemplateSyntaxError

if TYPE_CHECKING:
    from jinja2.lexer import TokenStream, Token

PathType = Union[PathLike, str]
PathTypeOrIter = Union[PathType, Iterable[PathType]]


def peek_tokens(stream: "TokenStream", n: int = 1) -> List["Token"]:
    """Peek ahead 'n' tokens in the token stream, but don't move the cursor

    Args:
        stream: The token stream
        n: n tokens to look at

    Returns:
        List of n tokens ahead.
    """
    out = []
    pushes = []
    for _ in range(n):
        out.append(next(stream))
        pushes.append(stream.current)

    for token in pushes:
        stream.push(token)
    stream.current = out[0]
    return out


def parse_tag_args(
    stream: "TokenStream", name: str, lineno: int
) -> nodes.Node:
    """Parse arguments for a tag.

    Only integer and name are allowed as values

    Examples:
        >>> "{{tablerow product in products cols:2}}"
        >>> parse_tag_args(stream, "cols", lineno)
        >>> # returns nodes.Const(2)

    Args:
        stream: The token stream
        name: The name of the argument
        lineno: The lineno

    Returns:
        None if the argument is not pressent otherwise a Const or Name node
    """
    # use Parser.parse_primary?
    arg = stream.skip_if(f"name:{name}")
    if not arg:
        return None

    stream.expect("colon")
    # tokens_ahead = peek_tokens(stream)
    if not stream.current.test_any(TOKEN_INTEGER, TOKEN_NAME):
        raise TemplateSyntaxError(
            f"Expected an integer or a variable as argument for '{name}'.",
            lineno,
        )

    arg = next(stream)
    if arg.type is TOKEN_INTEGER:
        return nodes.Const(arg.value)
    return nodes.Name(arg.value, "load")
