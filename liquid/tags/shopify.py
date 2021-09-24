"""Provide shopify tags
see: https://shopify.dev/api/liquid/tags
"""

from .manager import TagManager
from .standard import (
    comment,
    capture,
    assign,
    unless,
    case,
    tablerow,
    increment,
    decrement,
    cycle,
)


shopify_tags = TagManager()

shopify_tags.register(comment, raw=True)
shopify_tags.register(capture)
shopify_tags.register(assign)
shopify_tags.register(unless)
shopify_tags.register(case)
shopify_tags.register(tablerow)
shopify_tags.register(increment)
shopify_tags.register(decrement)
shopify_tags.register(cycle)

# https://shopify.dev/api/liquid/tags/theme-tags
# TODO: echo, form, layout, liquid, paginate, render, section, style
