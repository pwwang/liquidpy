"""Provides tags for wild mode"""
import textwrap

from jinja2 import nodes
from jinja2.environment import Environment
from jinja2.lexer import TOKEN_BLOCK_END, Token
from jinja2.parser import Parser

from .manager import TagManager, decode_raw
from .standard import assign, capture, case, comment, cycle

wild_tags = TagManager()

wild_tags.register(comment, raw=True)
wild_tags.register(case)
wild_tags.register(capture)
wild_tags.register(assign)
wild_tags.register(cycle)


@wild_tags.register(raw=True, env=True)
def python(env: Environment, token: Token, parser: Parser) -> nodes.Node:
    """The python tag

    {% python %} ... {% endpython %} or
    {% python ... %}

    The globals from the enviornment will be used to evaluate the code
    It also affect the globals from the environment

    Args:
        env: The environment
        token: The token matches the tag name
        parser: The parser

    Returns:
        The parsed node
    """
    if parser.stream.current.type is TOKEN_BLOCK_END:
        # expect {% endpython %}
        body = parser.parse_statements(("name:endpython",), drop_needle=True)
        body = decode_raw(body[0].nodes[0].data)
        body_parts = body.split("\n", 1)
        if not body_parts[0]:
            body = "" if len(body_parts) < 2 else body_parts[1]
        body = textwrap.dedent(body)
    else:
        pieces = []
        pieces_append = pieces.append
        while True:
            token = next(parser.stream)
            pieces_append(str(token.value))
            if parser.stream.current.type is TOKEN_BLOCK_END:
                break

        body = " ".join(pieces)

    code = compile(body, "<liquid-python-tag>", mode="exec")
    exec(code, env.globals)
    return nodes.Output([], lineno=token.lineno)


@wild_tags.register(env=True)
def import_(env: Environment, token: Token, parser: Parser) -> nodes.Node:
    """The import_ tag {% import_ ... %}

    Name it 'import_' so the 'import' tag from jinja can still work

    Args:
        env: The environment
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    pieces = ["import"]
    pieces_append = pieces.append
    while True:
        token = next(parser.stream)
        pieces_append(str(token.value))
        if parser.stream.current.type is TOKEN_BLOCK_END:
            break
    body = " ".join(pieces)
    code = compile(body, "<liquid-import_-tag>", mode="exec")
    exec(code, env.globals)
    return nodes.Output([], lineno=token.lineno)


@wild_tags.register(env=True)
def from_(env: Environment, token: Token, parser: Parser) -> nodes.Node:
    """The from_ tag {% from_ ... %}

    Name it 'from_' so the 'from_' tag from jinja can still work

    Args:
        env: The environment
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    pieces = ["from"]
    pieces_append = pieces.append
    while True:
        token = next(parser.stream)
        pieces_append(str(token.value))
        if parser.stream.current.type is TOKEN_BLOCK_END:
            break
    body = " ".join(pieces)
    code = compile(body, "<liquid-from_-tag>", mode="exec")
    exec(code, env.globals)
    return nodes.Output([], lineno=token.lineno)
