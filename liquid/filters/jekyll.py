"""Provides jekyll filters
See: https://jekyllrb.com/docs/liquid/filters/
"""
import datetime
import os
import random
import re
import urllib.parse
from typing import TYPE_CHECKING, Any, Sequence

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


def _getattr_multi(obj: Any, attr: str) -> Any:
    """Get attribute of an object at multiple levels

    For example: x.a.b = 1, _getattr_multi(x, "a.b") == 1
    """
    attrs = attr.split(".")
    for att in attrs:
        try:
            obj = _getattr(obj, att)
        except (TypeError, KeyError):
            obj = None
    return obj


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


@jekyll_filter_manager.register
def xml_escape(input: str) -> str:
    """Convert an object into its String representation

    Args:
        input: The object to be converted

    Returns:
        The converted string
    """
    if input is None:
        return ""

    from xml.sax.saxutils import escape
    return escape(input)


@jekyll_filter_manager.register
def cgi_escape(input: str) -> str:
    """CGI escape a string for use in a URL. Replaces any special characters
    with appropriate %XX replacements.

    Args:
        input: The string to escape

    Returns:
        The escaped string
    """
    return urllib.parse.quote_plus(input)


@jekyll_filter_manager.register
def uri_escape(input: str) -> str:
    """URI escape a string.

    Args:
        input: The string to escape

    Returns:
        The escaped string
    """
    return urllib.parse.quote(input, safe="!*'();:@&=+$,/?#[]")


# TODO: smartify, sassify, scssify


@jekyll_filter_manager.register
def jsonify(input: Any) -> str:
    """Convert the input into json string

    Args:
        input: The Array or Hash to be converted

    Returns:
        The converted json string
    """
    import json
    return json.dumps(input)


@jekyll_filter_manager.register
def array_to_sentence_string(
    array: Sequence[str],
    connector: str = "and",
) -> str:
    """Join an array of things into a string by separating with commas and the
    word "and" for the last one.

    Args:
        array: The Array of Strings to join.
        connector: Word used to connect the last 2 items in the array

    Returns:
        The formatted string.
    """
    if len(array) == 0:
        return ""

    array = [str(elm) for elm in array]
    if len(array) == 1:
        return array[0]

    if len(array) == 2:
        return f"{array[0]} {connector} {array[1]}"

    return ", ".join(array[:-1]) + f", {connector} {array[-1]}"


@jekyll_filter_manager.register("slugify")
def jekyll_slugify(input: str, mode: str = "default") -> str:
    """Slugify a string

    Note that non-ascii characters are always translated to ascii ones.

    Args:
        input: The input string
        mode: How string is slugified

    Returns:
        The slugified string
    """
    if input is None or mode == "none":
        return input

    from slugify import slugify  # type: ignore

    if mode == "pretty":
        return slugify(input, regex_pattern=r"[^_.~!$&'()+,;=@\w]+")
    if mode == "raw":
        return slugify(input, regex_pattern=r"\s+")

    return slugify(input)


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
        return len(regex.findall(cjk_regex, input)) + len(
            regex.findall(word_regex, input)
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


@jekyll_filter_manager.register("sort")
def jekyll_sort(
    array: Sequence,
    prop: str = None,
    none_pos: str = "first",
) -> Sequence:
    """Sort an array in a reverse way by default.

    Note that the order might be different than it with ruby. For example,
    in python `"1abc" > "1"`, but it's not the case in jekyll. Also, it's
    always in reverse order for property values.

    Args:
        array: The array
        prop: property name
        none_pos: None order (first or last).

    Returns:
        The sorted array
    """
    if array is None:
        raise ValueError("Cannot sort None object.")

    if none_pos not in ("first", "last"):
        raise ValueError(
            f"{none_pos!r} is not a valid none_pos order. "
            "It must be 'first' or 'last'."
        )

    if prop is None:
        non_none_arr = [elm for elm in array if elm is not None]
        n_none = len(array) - len(non_none_arr)
        sorted_arr = list(sorted(non_none_arr, reverse=True))

        if none_pos == "first":
            return [None] * n_none + sorted_arr

        return sorted_arr + [None] * n_none

    non_none_arr = [
        elm for elm in array if _getattr_multi(elm, prop) is not None
    ]
    none_arr = [elm for elm in array if _getattr_multi(elm, prop) is None]
    sorted_arr = list(
        sorted(
            non_none_arr,
            key=lambda elm: _getattr_multi(elm, prop),
            reverse=True,
        )
    )

    if none_pos == "first":
        return none_arr + sorted_arr

    return sorted_arr + none_arr


@jekyll_filter_manager.register
def sample(value, n: int = 1):
    """Sample elements from array"""
    return random.sample(value, k=n)
