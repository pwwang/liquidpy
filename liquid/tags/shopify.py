"""Provide shopify tags
see: https://shopify.dev/api/liquid/tags
"""

from .manager import TagManager
from jinja2 import nodes
from .standard import (
    comment,
    inline_comment,
    capture,
    assign,
    unless,
    case,
    tablerow as standard_tablerow,
    increment,
    decrement,
    cycle,
)


shopify_tags = TagManager()

shopify_tags.register(comment, raw=True)
shopify_tags.register(inline_comment, raw=True)
shopify_tags.register(capture)
shopify_tags.register(assign)
shopify_tags.register(unless)
shopify_tags.register(case)
shopify_tags.register(increment)
shopify_tags.register(decrement)
shopify_tags.register(cycle)


def tablerow(token, parser):
    node = standard_tablerow(token, parser)
    if isinstance(node, list) and node and isinstance(node[0], nodes.Output):
        node[0].nodes[1] = nodes.Const(1)
    _format_tablerow(node)
    return node


def _format_tablerow(node):
    if isinstance(node, list):
        for child in node:
            _format_tablerow(child)
        return
    if isinstance(node, nodes.Output):
        if (
            node.nodes
            and isinstance(node.nodes[0], nodes.Const)
            and isinstance(node.nodes[0].value, str)
            and node.nodes[0].value.startswith('<tr class="row')
        ):
            last = node.nodes[-1]
            if isinstance(last, nodes.Const):
                last.value += "\n"
        elif (
            len(node.nodes) == 1
            and isinstance(node.nodes[0], nodes.Const)
            and node.nodes[0].value.endswith("</tr>")
        ):
            node.nodes[0].value += "\n"
    for child in node.iter_child_nodes():
        _format_tablerow(child)


shopify_tags.register(tablerow)


# https://shopify.dev/api/liquid/tags/theme-tags
# TODO: echo, form, layout, liquid, paginate, render, section, style
