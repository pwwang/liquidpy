"""Provides standard liquid filters"""
import re
import math
import html
from datetime import datetime

from jinja2.filters import FILTERS

from .manager import FilterManager


standard_filter_manager = FilterManager()


class DateTime:
    """Date time allows plus/minus operation"""
    def __init__(self, dt: datetime, fmt: str) -> None:
        self.dt = dt
        self.fmt = fmt

    def __str__(self) -> str:
        """How it is rendered"""
        return self.dt.strftime(self.fmt)

    def __add__(self, other: int) -> int:
        return int(str(self)) + other

    def __sub__(self, other: int) -> int:
        return int(str(self)) - other

    def __mul__(self, other: int) -> int:
        return int(str(self)) * other

    def __floordiv__(self, other: int) -> float:
        return float(str(self)) // other

    def __mod__(self, other: int) -> int:
        return int(str(self)) % other

    def __pow__(self, other: int) -> int:  # pragma: no cover
        return int(str(self)) ** other

    def __truediv__(self, other: int) -> float:  # pragma: no cover
        return float(str(self)) / other

    def __radd__(self, other: int) -> int:  # pragma: no cover
        return other + int(str(self))

    def __rsub__(self, other: int) -> int:  # pragma: no cover
        return other - int(str(self))

    def __rmul__(self, other: int) -> int:  # pragma: no cover
        return other * int(str(self))

    def __rmod__(self, other: int) -> int:  # pragma: no cover
        return other % int(str(self))

    def __rpow__(self, other: int) -> int:  # pragma: no cover
        return other ** int(str(self))

    def __rtruediv__(self, other: int) -> float:  # pragma: no cover
        return other / float(str(self))

    def __rfloordiv__(self, other: int) -> float:  # pragma: no cover
        return other // float(str(self))


class EmptyDrop:
    """The EmptyDrop class borrowed from liquid"""

    # Use jinja's Undefined instead?

    def __init__(self):
        setattr(self, "empty?", True)

    def __str__(self):
        return ""

    def __eq__(self, other):
        return not bool(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return False


def _get_prop(obj, prop, _raise=False):
    """Get the property of the object, allow via getitem"""
    try:
        return obj[prop]
    except (TypeError, KeyError):
        try:
            return getattr(obj, prop)
        except AttributeError:
            if _raise:  # pragma: no cover
                raise
            return None


# Jinja comes with thses filters
# standard_filter_manager.register(str.capitalize)
# standard_filter_manager.register(abs)
# standard_filter_manager.register(round)
standard_filter_manager.register("concat")(list.__add__)
standard_filter_manager.register("at_least")(max)
standard_filter_manager.register("at_most")(min)
standard_filter_manager.register("downcase")(str.lower)
standard_filter_manager.register("upcase")(str.upper)
standard_filter_manager.register(html.escape)
standard_filter_manager.register(str.lstrip)
standard_filter_manager.register(str.rstrip)
standard_filter_manager.register(str.strip)
standard_filter_manager.register(str.replace)
standard_filter_manager.register("size")(len)
standard_filter_manager.register(int)
standard_filter_manager.register(float)
standard_filter_manager.register(str)
standard_filter_manager.register(bool)


@standard_filter_manager.register
def split(base, sep):
    """Split a string into a list
    If the sep is empty, return the list of characters
    """
    if not sep:
        return list(base)
    return base.split(sep)


@standard_filter_manager.register
def append(base, suffix):
    """Append a suffix to a string"""
    return f"{base}{suffix}"


@standard_filter_manager.register
def prepend(base, prefix):
    """Prepend a prefix to a string"""
    return f"{prefix}{base}"


@standard_filter_manager.register
def times(base, sep):
    """Implementation of *"""
    return base * sep


@standard_filter_manager.register
def minus(base, sep):
    """Implementation of -"""
    return base - sep


@standard_filter_manager.register
def plus(base, sep):
    """Implementation of +"""
    return base + sep


@standard_filter_manager.register
def modulo(base, sep):
    """Implementation of %"""
    return base % sep


@standard_filter_manager.register
def ceil(base):
    """Get the ceil of a number"""
    return math.ceil(float(base))


@standard_filter_manager.register
def floor(base):
    """Get the floor of a number"""
    return math.floor(float(base))


@standard_filter_manager.register("date")
def liquid_date(base, fmt):
    """Format a date/datetime"""

    if base == "now":
        dtime = datetime.now()
    elif base == "today":
        dtime = datetime.today()
    elif isinstance(base, (int, float)):
        dtime = datetime.fromtimestamp(base)
    else:
        from dateutil import parser    # type: ignore
        dtime = parser.parse(base)

    return DateTime(dtime, fmt)


@standard_filter_manager.register
def default(base, deft, allow_false=False):
    """Return the deft value if base is not set.
    Otherwise, return base"""
    if allow_false and base is False:
        return False
    if base is None:
        return deft
    return FILTERS["default"](base, deft, isinstance(base, str))


@standard_filter_manager.register
def divided_by(base, dvdby):
    """Implementation of / or //"""
    if isinstance(dvdby, int):
        return base // dvdby
    return base / dvdby


@standard_filter_manager.register
def escape_once(base):
    """Escapse html characters only once of the string"""
    return html.escape(html.unescape(base))


@standard_filter_manager.register
def newline_to_br(base):
    """Replace newline with `<br />`"""
    return base.replace("\n", "<br />")


@standard_filter_manager.register
def remove(base, string):
    """Remove a substring from a string"""
    return base.replace(string, "")


@standard_filter_manager.register
def remove_first(base, string):
    """Remove the first substring from a string"""
    return base.replace(string, "", 1)


@standard_filter_manager.register
def replace_first(base, old, new):
    """Replace the first substring with new string"""
    return base.replace(old, new, 1)


# @standard_filter_manager.register
# def reverse(base):
#     """Get the reversed list"""
#     if not base:
#         return EmptyDrop()
#     return list(reversed(base))


@standard_filter_manager.register
def sort(base):
    """Get the sorted list"""
    if not base:
        return EmptyDrop()
    return list(sorted(base))


@standard_filter_manager.register
def sort_natural(base):
    """Get the sorted list in a case-insensitive manner"""
    if not base:
        return EmptyDrop()
    return list(sorted(base, key=str.casefold))


@standard_filter_manager.register("slice")
def liquid_slice(base, start, length=1):
    """Slice a list"""
    if not base:
        return EmptyDrop()
    if start < 0:
        start = len(base) + start
    end = None if length is None else start + length
    return base[start:end]


@standard_filter_manager.register
def strip_html(base):
    """Strip html tags from a string"""
    # use html parser?
    return re.sub(r"<[^>]+>", "", base)


@standard_filter_manager.register
def strip_newlines(base):
    """Strip newlines from a string"""
    return base.replace("\n", "")


@standard_filter_manager.register
def truncate(base, length, ellipsis="..."):
    """Truncate a string"""
    lenbase = len(base)
    if length >= lenbase:
        return base

    return base[: length - len(ellipsis)] + ellipsis


@standard_filter_manager.register
def truncatewords(base, length, ellipsis="..."):
    """Truncate a string by words"""
    # do we need to preserve the whitespaces?
    baselist = base.split()
    lenbase = len(baselist)
    if length >= lenbase:
        return base

    # instead of collapsing them into just a single space?
    return " ".join(baselist[:length]) + ellipsis


@standard_filter_manager.register
def uniq(base):
    """Get the unique elements from a list"""
    if not base:
        return EmptyDrop()
    ret = []
    for bas in base:
        if bas not in ret:
            ret.append(bas)
    return ret


@standard_filter_manager.register
def url_decode(base):
    """Url-decode a string"""
    try:
        from urllib import unquote
    except ImportError:
        from urllib.parse import unquote
    return unquote(base)


@standard_filter_manager.register
def url_encode(base):
    """Url-encode a string"""
    try:
        from urllib import urlencode
    except ImportError:
        from urllib.parse import urlencode
    return urlencode({"": base})[1:]


@standard_filter_manager.register
def where(base, prop, value):
    """Query a list of objects with a given property value"""
    ret = [bas for bas in base if _get_prop(bas, prop) == value]
    return ret or EmptyDrop()


@standard_filter_manager.register(["liquid_map", "map"])
def liquid_map(base, prop):
    """Map a property to a list of objects"""
    return [_get_prop(bas, prop) for bas in base]


@standard_filter_manager.register
def attr(base, prop):
    """Similar as `__getattr__()` but also works like `__getitem__()"""
    return _get_prop(base, prop)


# @standard_filter_manager.register
# def join(base, sep):
#     """Join a list by the sep"""
#     if isinstance(base, EmptyDrop):
#         return ''
#     return sep.join(base)

# @standard_filter_manager.register
# def first(base):
#     """Get the first element of the list"""
#     if not base:
#         return EmptyDrop()
#     return base[0]

# @standard_filter_manager.register
# def last(base):
#     """Get the last element of the list"""
#     if not base:
#         return EmptyDrop()
#     return base[-1]


@standard_filter_manager.register
def compact(base):
    """Remove empties from a list"""
    ret = [bas for bas in base if bas]
    return ret or EmptyDrop()


@standard_filter_manager.register
def regex_replace(
    base: str,
    regex: str,
    replace: str = "",
    case_sensitive: bool = False,
    count: int = 0,
) -> str:
    """Replace matching regex pattern"""
    if not isinstance(base, str):
        # Raise an error instead?
        return base

    args = {
        "pattern": regex,  # re.escape
        "repl": replace,
        "string": base,
        "count": count,
    }
    if not case_sensitive:
        args["flags"] = re.IGNORECASE

    return re.sub(**args)    # type: ignore
