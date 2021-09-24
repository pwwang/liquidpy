"""Provides jekyll tags"""
import os

from jinja2 import nodes
from jinja2.lexer import Token
from jinja2.parser import Parser

from .manager import TagManager
from .standard import (
    assign,
    capture,
    case,
    comment,
    cycle,
    decrement,
    increment,
    tablerow,
    unless,
)


jekyll_tags = TagManager()

jekyll_tags.register(comment, raw=True)
jekyll_tags.register(capture)
jekyll_tags.register(assign)
jekyll_tags.register(unless)
jekyll_tags.register(case)
jekyll_tags.register(tablerow)
jekyll_tags.register(increment)
jekyll_tags.register(decrement)
jekyll_tags.register(cycle)


# to specify certain named arguments
# use jinja's with
# https://stackoverflow.com/a/9405157/5088165
@jekyll_tags.register
def include_relative(token: Token, parser: Parser) -> nodes.Node:
    """The {% include_relative ... %} tag"""
    node = nodes.Include(lineno=token.lineno)
    path = parser.parse_expression()
    if parser.stream.filename:
        node.template = nodes.Add(
            nodes.Add(
                nodes.Const(os.path.dirname(parser.stream.filename)),
                nodes.Const(os.path.sep),
            ),
            path,
        )
    else:
        node.template = path

    node.ignore_missing = False
    return parser.parse_import_context(node, True)
