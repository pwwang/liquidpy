"""Provides jekyll filters
See: https://jekyllrb.com/docs/liquid/filters/
"""
import datetime
import os
import random
import re
import urllib.parse
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from jinja2.environment import Environment


# environmentfilter deprecated
try:
    from jinja2 import pass_environment
except ImportError:
    from jinja2 import environmentfilter as pass_environment

from jinja2.filters import FILTERS

from .manager import FilterManager

jekyll_filter_manager = FilterManager()


def _getattr(obj: Any, attr: str) -> Any:
    """Get attribute of an object, if fails, try get item"""
    try:
        return getattr(obj, attr)
    except AttributeError:
        return obj[attr]


def _get_global_var(env: "Environment", name: str, attr: str = None) -> Any:
    if name not in env.globals:
        raise ValueError(f"Global variables has not been set: {name}")

    out = env.globals[name]
    if attr is None:  # pragma: no cover
        return out

    return _getattr(out, attr)


jekyll_filter_manager.register("group_by")(FILTERS["groupby"])
jekyll_filter_manager.register("to_integer")(FILTERS["int"])
jekyll_filter_manager.register("inspect")(repr)


@jekyll_filter_manager.register
@pass_environment
def relative_url(env, value):
    """Get relative url based on site.baseurl"""
    baseurl = _get_global_var(env, "site", "baseurl")
    parts = urllib.parse.urlparse(baseurl)
    return os.path.join(parts.path, value)


@jekyll_filter_manager.register
@pass_environment
def absolute_url(env, value):
    """Get absolute url based on site.baseurl"""
    baseurl = _get_global_var(env, "site", "baseurl")
    return urllib.parse.urljoin(baseurl, value)


@jekyll_filter_manager.register
@pass_environment
def date_to_xmlschema(env, value: datetime.datetime):
    """Convert date to xml schema format"""
    return value.isoformat()


# TODO: other date filters


@jekyll_filter_manager.register
@pass_environment
def where_exp(env, value, item, expr):
    """Where using expression"""
    compiled = env.compile_expression(expr)
    return [itm for itm in value if compiled(**{item: itm})]


@jekyll_filter_manager.register
def find(value, attr, query):
    """Find elements from array using attribute value"""
    for item in value:
        try:
            if _getattr(item, attr) == query:
                return item
        except (KeyError, AttributeError):
            continue
    return None


@jekyll_filter_manager.register
@pass_environment
def find_exp(env, value, item, expr):
    """Find elements using expression"""
    compiled = env.compile_expression(expr)
    for itm in value:
        try:
            test = compiled(**{item: itm})
        except AttributeError:
            continue
        if test:
            return itm
    return None


@jekyll_filter_manager.register
@pass_environment
def group_by_expr(env, value, item, expr):
    """Group by data using expression"""
    compiled = env.compile_expression(expr)
    out = {}
    for itm in value:
        name = compiled(**{item: itm})
        out.setdefault(name, []).append(itm)
    return [{name: name, items: items} for name, items in out.items()]

# TODO: xml_escape, cgi_escape, uri_escape
# TODO: array_to_sentence_string
# TODO: smartify, sassify, scssify
# TODO: slugify, jsonify


@jekyll_filter_manager.register
def number_of_words(input: str, mode: str = None) -> int:
    """Count the number of words in the input string.

    Args:
        input: The String on which to operate.
        mode: Passing 'cjk' as the argument will count every CJK character
            detected as one word irrespective of being separated by whitespace.
            Passing 'auto' (auto-detect) works similar to 'cjk'

    Returns:
        The word count.
    """
    import regex
    cjk_charset = r"\p{Han}\p{Katakana}\p{Hiragana}\p{Hangul}"
    cjk_regex = fr"[{cjk_charset}]"
    word_regex = fr"[^{cjk_charset}\s]+"
    if mode == "cjk":
        return (
            len(regex.findall(cjk_regex, input))
            + len(regex.findall(word_regex, input))
        )
    if mode == "auto":
        cjk_count = len(regex.findall(cjk_regex, input))
        return (
            len(input.split())
            if cjk_count == 0
            else cjk_count + len(regex.findall(word_regex, input))
        )
    return len(input.split())


@jekyll_filter_manager.register
def markdownify(value):
    """Markdownify a string"""
    from markdown import markdown  # type: ignore
    return markdown(value)


@jekyll_filter_manager.register
def normalize_whitespace(value):
    """Replace multiple spaces into one"""
    return re.sub(r"\s+", " ", value)


# TODO: sort


@jekyll_filter_manager.register
def sample(value, n: int = 1):
    """Sample elements from array"""
    return random.sample(value, k=n)
