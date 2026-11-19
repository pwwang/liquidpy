"""Provides shopify filters"""

import re
from collections.abc import Mapping
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import unquote_plus

from jinja2 import Undefined

from .standard import _get_prop
from .manager import FilterManager


shopify_filter_manager = FilterManager()


class _ShopifyDrop:
    def __init__(self, name):
        self.name = name

    def __bool__(self):
        return False

    def __str__(self):
        return ""

    def __eq__(self, other):
        if self.name == "blank":
            return (
                other is None
                or isinstance(other, Undefined)
                or other is False
                or other == ""
                or isinstance(other, (list, tuple, dict)) and not other
            )
        return (
            other == ""
            or isinstance(other, (list, tuple, dict)) and not other
        )


blank = _ShopifyDrop("blank")
empty = _ShopifyDrop("empty")
_MISSING = object()


def liquid_equal(left, right):
    """Compare Liquid values without treating booleans as numbers."""
    if isinstance(left, _ShopifyDrop):
        return left == right
    if isinstance(right, _ShopifyDrop):
        return right == left
    if isinstance(left, Undefined):
        left = None
    if isinstance(right, Undefined):
        right = None
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    return left == right


def liquid_contains(container, value):
    """Check Liquid membership using Liquid's value equality."""
    if isinstance(container, str):
        return isinstance(value, str) and value in container
    try:
        return any(liquid_equal(item, value) for item in container)
    except TypeError:
        return False


@shopify_filter_manager.register
def at_least(base, other):
    if isinstance(other, Undefined) or other is None:
        return base
    if isinstance(base, Undefined) or base is None:
        return other
    return max(base, other)


@shopify_filter_manager.register
def divided_by(base, divisor):
    if isinstance(divisor, int) and not isinstance(divisor, bool):
        if isinstance(base, float):
            return base / divisor
        return base // divisor
    return base / divisor


@shopify_filter_manager.register
def round(base, precision=0):
    places = int(precision)
    rounded = Decimal(str(base)).quantize(
        Decimal(1).scaleb(-places),
        rounding=ROUND_HALF_UP,
    )
    return int(rounded) if places == 0 else float(rounded)


@shopify_filter_manager.register
def liquid_map(base, prop):
    if isinstance(base, Mapping):
        return [base[prop]] if prop in base else []
    return [_get_prop(item, prop) for item in base]


@shopify_filter_manager.register("map")
def shopify_map(base, prop):
    return liquid_map(base, prop)


@shopify_filter_manager.register
def sort(base):
    if isinstance(base, str):
        return "".join(sorted(base))
    return sorted(base)


@shopify_filter_manager.register
def where(base, prop, value):
    return [item for item in base if liquid_equal(_get_prop(item, prop), value)]


@shopify_filter_manager.register
def reject(base, prop, value=_MISSING):
    if value is _MISSING:
        return [item for item in base if not _get_prop(item, prop)]
    return [
        item for item in base if not liquid_equal(_get_prop(item, prop), value)
    ]


@shopify_filter_manager.register
def newline_to_br(base):
    return base.replace("\n", "<br />\n")


@shopify_filter_manager.register
def strip_html(base):
    base = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1\s*>",
        "",
        base,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return re.sub(r"<[^>]+>", "", base)


@shopify_filter_manager.register
def url_decode(base):
    return unquote_plus(base)


# TODO: color filters
# https://shopify.dev/api/liquid/filters/color-filters

# TODO: font filters
# https://shopify.dev/api/liquid/filters/font-filters

# TODO: html filters
# https://shopify.dev/api/liquid/filters/html-filters

# TODO: media filters
# https://shopify.dev/api/liquid/filters/media-filters

# TODO: metafield filters
# https://shopify.dev/api/liquid/filters/metafield-filters

# TODO: money filters
# https://shopify.dev/api/liquid/filters/money-filters

# TODO: string filters
# https://shopify.dev/api/liquid/filters/string-filters

# TODO: url filters
# https://shopify.dev/api/liquid/filters/url-filters

# TODO: additional filters
# https://shopify.dev/api/liquid/filters/additional-filters
