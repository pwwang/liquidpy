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
        return True

    def __str__(self):
        return ""

    def __eq__(self, other):
        if isinstance(other, _ShopifyDrop):
            return self.name == other.name
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

    def __add__(self, other):
        return other

    __radd__ = __add__

    def split(self, _separator=None):
        return []

    def __iter__(self):
        return iter(())


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
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return left.keys() == right.keys() and all(
            liquid_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, type(left)):
        return len(left) == len(right) and all(
            liquid_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def liquid_contains(container, value):
    """Check Liquid membership using Liquid's value equality."""
    if value is None or isinstance(value, Undefined) or isinstance(value, bool):
        return False
    if isinstance(container, str):
        return isinstance(value, str) and value in container
    try:
        return any(liquid_equal(item, value) for item in container)
    except TypeError:
        return False


def _shopify_prop(item, prop):
    if isinstance(item, Mapping):
        return item.get(prop)
    if isinstance(item, str):
        return None
    value = _get_prop(item, prop)
    return None if callable(value) else value


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
    if isinstance(base, Undefined) or base is None:
        return 0
    try:
        places = 0 if isinstance(precision, Undefined) else int(float(precision))
    except (TypeError, ValueError):
        places = 0
    rounded = Decimal(str(base)).quantize(
        Decimal(1).scaleb(-places),
        rounding=ROUND_HALF_UP,
    )
    return int(rounded) if places <= 0 else float(rounded)


@shopify_filter_manager.register
def liquid_map(base, prop):
    if isinstance(base, Undefined) or base is None or isinstance(prop, Undefined):
        return []
    if isinstance(base, Mapping):
        return [base[prop]] if prop in base else []
    return [_shopify_prop(item, prop) for item in base]


@shopify_filter_manager.register("map")
def shopify_map(base, prop):
    return liquid_map(base, prop)


@shopify_filter_manager.register
def sort(base, prop=None):
    if isinstance(base, str):
        return base
    if isinstance(base, Undefined) or base is None:
        return []
    try:
        if prop is None or isinstance(prop, Undefined):
            return sorted(base)
        return sorted(base, key=lambda item: _shopify_prop(item, prop))
    except TypeError:
        return None


@shopify_filter_manager.register
def where(base, prop, value=_MISSING):
    if isinstance(base, Undefined) or base is None:
        return []
    if value is _MISSING or value is None or isinstance(value, Undefined):
        return [item for item in base if _liquid_truthy(_shopify_prop(item, prop))]
    return [item for item in base if liquid_equal(_shopify_prop(item, prop), value)]


@shopify_filter_manager.register
def reject(base, prop, value=_MISSING):
    if isinstance(base, Undefined) or base is None:
        return []
    if isinstance(base, str):
        base = [base]
    if value is _MISSING or value is None or isinstance(value, Undefined):
        return [
            item for item in base if not _liquid_truthy(_reject_prop(item, prop))
        ]
    return [
        item for item in base if not liquid_equal(_reject_prop(item, prop), value)
    ]


def _reject_prop(item, prop):
    if isinstance(item, str):
        return prop in item
    return _shopify_prop(item, prop)


def _liquid_truthy(value):
    return value is not None and not isinstance(value, Undefined) and value is not False


@shopify_filter_manager.register("join")
def shopify_join(base, separator=" ", attribute=None):
    if isinstance(base, str):
        return base
    if isinstance(base, Undefined) or base is None:
        return ""
    return separator.join(
        "" if value is None or isinstance(value, Undefined)
        else str(_get_prop(value, attribute)) if attribute is not None
        else str(value)
        for value in base
    )


@shopify_filter_manager.register("truncatewords")
def shopify_truncatewords(base, length, ellipsis="..."):
    words = base.split()
    length = max(1, int(length))
    if length >= len(words):
        return base
    return " ".join(words[:length]) + ellipsis


@shopify_filter_manager.register("slice")
def shopify_slice(base, start, length=1):
    if isinstance(base, range):
        base = f"{base.start}..{base.stop - 1}"
    if not base:
        return ""
    if start < 0:
        start = len(base) + start
    end = None if length is None else start + length
    return base[start:end]


@shopify_filter_manager.register
def newline_to_br(base):
    return base.replace("\n", "<br />\n")


@shopify_filter_manager.register("lstrip")
def shopify_lstrip(base):
    if isinstance(base, Undefined) or base is None:
        return ""
    return str(base).replace("\ue000", "\r").lstrip()


@shopify_filter_manager.register("rstrip")
def shopify_rstrip(base):
    if isinstance(base, Undefined) or base is None:
        return ""
    return str(base).replace("\ue000", "\r").rstrip()


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
