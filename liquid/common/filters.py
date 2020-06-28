import math
from ..filtermgr import register_filter

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
    except KeyError:
        return getattr(obj, prop)

@register_filter
def split(base, sep):
    if not sep:
        return list(base)
    return base.split(sep)

@register_filter
def append(base, suffix):
    return f"{base}{suffix}"

@register_filter
def prepend(base, prefix):
    return f"{prefix}{base}"

@register_filter
def ceil(base):
    return math.ceil(float(base))

@register_filter
def floor(base):
    return math.floor(float(base))

@register_filter('map')
def liquid_map(base, prop):
    return [_get_prop(bas, prop) for bas in base]

@register_filter
def compact(base):
    return [bas for bas in base if bas]

@register_filter('date')
def liquid_date(base, fmt):
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
    if base == 0.0:
        return base
    return base or deft

@register_filter
def divided_by(base, dvdby):
    if isinstance(dvdby, int):
        return base // dvdby
    return base / dvdby

@register_filter
def escape_once(base):
    import html
    return html.escape(html.unescape(base))

@register_filter
def first(base):
    return base[0]

@register_filter
def last(base):
    return base[-1]

@register_filter
def join(base, sep):
    return sep.join(base)

@register_filter
def minus(base, sep):
    return base - sep

@register_filter
def plus(base, sep):
    return base + sep

@register_filter
def times(base, sep):
    return base * sep

@register_filter
def modulo(base, sep):
    return base % sep

@register_filter
def newline_to_br(base):
    return base.replace('\n', '<br />')

@register_filter
def remove(base, string):
    return base.replace(string, '')

@register_filter
def remove_first(base, string):
    return base.replace(string, '', 1)

@register_filter
def replace_first(base, old, new):
    return base.replace(old, new, 1)

@register_filter
def reverse(base):
    return list(reversed(base))

@register_filter
def sort(base):
    return list(sorted(base))

@register_filter
def sort_natural(base):
    return list(sorted(base, key=str.casefold))

@register_filter('slice')
def liquid_slice(base, start, length=1):
    if start < 0:
        start = len(base) + start
    return base[start:start+length]

@register_filter
def strip_html(base):
    import re
    # use html parser?
    return re.sub(r'<[^>]+>', '', base)

@register_filter
def strip_newlines(base):
    return base.replace('\n', '')

@register_filter
def truncate(base, length, ellipsis="..."):
    lenbase = len(base)
    if length >= lenbase:
        return base

    return base[:length - len(ellipsis)] + ellipsis

@register_filter
def truncatewords(base, length, ellipsis="..."):
    base = base.split()
    lenbase = len(base)
    if length >= lenbase:
        return base

    return " ".join(base[:length]) + ellipsis

@register_filter
def uniq(base):
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
    """Url-decode a string"""
    try:
        from urllib import urlencode
    except ImportError:
        from urllib.parse import urlencode
    return urlencode({'': base})[1:]

@register_filter
def where(base, prop, value):
    return [bas for bas in base if _get_prop(base, prop) == value]
