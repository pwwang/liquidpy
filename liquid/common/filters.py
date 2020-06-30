"""All filters from shopify's liquid"""
import math
from ..filtermgr import register_filter

class EmptyDrop:

    def __init__(self):
        setattr(self, 'empty?', True)

    def __str__(self):
        return ''

    def __eq__(self, other):
        return not bool(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False


register_filter(str.capitalize)
register_filter(abs)
register_filter('at_least')(max)
register_filter('at_most')(min)
register_filter('concat')(list.__add__)
register_filter(round)
register_filter('downcase')(str.lower)
register_filter('upcase')(str.upper)
register_filter(__import__('html').escape)
register_filter(str.lstrip)
register_filter(str.rstrip)
register_filter(str.strip)
register_filter(str.replace)
register_filter('size')(len)

def _get_prop(obj, prop):
    try:
        return obj[prop]
    except (TypeError, KeyError):
        return getattr(obj, prop)

@register_filter
def split(base, sep):
    """Split a string into a list
    If the sep is empty, return the list of characters
    """
    if not sep:
        return list(base)
    return base.split(sep)

@register_filter
def append(base, suffix):
    """Append a suffix to a string"""
    return f"{base}{suffix}"

@register_filter
def prepend(base, prefix):
    """Prepend a prefix to a string"""
    return f"{prefix}{base}"

@register_filter
def ceil(base):
    """Get the ceil of a number"""
    return math.ceil(float(base))

@register_filter
def floor(base):
    """Get the floor of a number"""
    return math.floor(float(base))

@register_filter('map')
def liquid_map(base, prop):
    """Map a property to a list of objects"""
    return [_get_prop(bas, prop) for bas in base]

@register_filter
def compact(base):
    """Remove empties from a list"""
    ret = [bas for bas in base if bas]
    return ret or EmptyDrop()

@register_filter('date')
def liquid_date(base, fmt):
    """Format a date/datetime"""
    from datetime import datetime
    if base == "now":
        dtime = datetime.now()
    elif base == "today":
        dtime = datetime.today()
    else:
        from dateutil import parser
        dtime = parser.parse(base)
    return dtime.strftime(fmt)

@register_filter
def default(base, deft):
    """Return the deft value if base is not set.
    Otherwise, return base"""
    if base == 0.0:
        return base
    return base or deft

@register_filter
def divided_by(base, dvdby):
    """Implementation of / or // """
    if isinstance(dvdby, int):
        return base // dvdby
    return base / dvdby

@register_filter
def escape_once(base):
    """Escapse html characters only once of the string"""
    import html
    return html.escape(html.unescape(base))

@register_filter
def first(base):
    """Get the first element of the list"""
    if not base:
        return EmptyDrop()
    return base[0]

@register_filter
def last(base):
    """Get the last element of the list"""
    if not base:
        return EmptyDrop()
    return base[-1]

@register_filter
def join(base, sep):
    """Join a list by the sep"""
    if isinstance(base, EmptyDrop):
        return ''
    return sep.join(base)

@register_filter
def minus(base, sep):
    """Implementation of - """
    return base - sep

@register_filter
def plus(base, sep):
    """Implementation of + """
    return base + sep

@register_filter
def times(base, sep):
    """Implementation of * """
    return base * sep

@register_filter
def modulo(base, sep):
    """Implementation of % """
    return base % sep

@register_filter
def newline_to_br(base):
    """Replace newline with `<br />`"""
    return base.replace('\n', '<br />')

@register_filter
def remove(base, string):
    """Remove a substring from a string"""
    return base.replace(string, '')

@register_filter
def remove_first(base, string):
    """Remove the first substring from a string"""
    return base.replace(string, '', 1)

@register_filter
def replace_first(base, old, new):
    """Replace the first substring with new string"""
    return base.replace(old, new, 1)

@register_filter
def reverse(base):
    """Get the reversed list"""
    if not base:
        return EmptyDrop()
    return list(reversed(base))

@register_filter
def sort(base):
    """Get the sorted list"""
    if not base:
        return EmptyDrop()
    return list(sorted(base))

@register_filter
def sort_natural(base):
    """Get the sorted list in a case-insensitive manner"""
    if not base:
        return EmptyDrop()
    return list(sorted(base, key=str.casefold))

@register_filter('slice')
def liquid_slice(base, start, length=1):
    """Slice a list"""
    if not base:
        return EmptyDrop()
    if start < 0:
        start = len(base) + start
    return base[start:start+length]

@register_filter
def strip_html(base):
    """Strip html tags from a string"""
    import re
    # use html parser?
    return re.sub(r'<[^>]+>', '', base)

@register_filter
def strip_newlines(base):
    """Strip newlines from a string"""
    return base.replace('\n', '')

@register_filter
def truncate(base, length, ellipsis="..."):
    """Truncate a string"""
    lenbase = len(base)
    if length >= lenbase:
        return base

    return base[:length - len(ellipsis)] + ellipsis

@register_filter
def truncatewords(base, length, ellipsis="..."):
    """Truncate a string by words"""
    # do we need to preserve the whitespaces?
    baselist = base.split()
    lenbase = len(baselist)
    if length >= lenbase:
        return base

    # instead of collapsing them into just a single space?
    return " ".join(baselist[:length]) + ellipsis

@register_filter
def uniq(base):
    """Get the unique elements from a list"""
    if not base:
        return EmptyDrop()
    ret = []
    for bas in base:
        if not bas in ret:
            ret.append(bas)
    return ret

@register_filter
def url_decode(base):
    """Url-decode a string"""
    try:
        from urllib import unquote
    except ImportError:
        from urllib.parse import unquote
    return unquote(base)

@register_filter
def url_encode(base):
    """Url-encode a string"""
    try:
        from urllib import urlencode
    except ImportError:
        from urllib.parse import urlencode
    return urlencode({'': base})[1:]

@register_filter
def where(base, prop, value):
    """Query a list of objects with a given property value"""
    ret = [bas for bas in base if _get_prop(bas, prop) == value]
    return ret or EmptyDrop()
