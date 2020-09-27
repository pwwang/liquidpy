"""The filters used in liquidpy

Attributes:
    filter_manager: The filter manager
"""
import math
import html
from .utils import Singleton
from .exceptions import LiquidFilterRegistryException

class FilterManager(Singleton):
    """A manager for filters

    Attributes:
        INSTANCE: The instance of the class, since it's a signleton
        filters: The filters database
    """

    INSTANCE = None     # type: FilterManager
    filters = {}        # type: Dict[str, Callable]

    def register(self, name_or_filter=None, mode='standard'):
        # type: (Optional[Union[str, Callable]], bool) -> Optional[Callable]
        """Register a filter

        This can be used as a decorator
        >>> @filter_manager.register
        >>> def add(a, b):
        >>>   return a+b
        >>> # register it with an alias:
        >>> @filter_manager.register('addfunc')
        >>> def add(a, b):
        >>>   return a+b

        Args:
            name_or_filter: The filter to register
                if name is given, will be treated as alias
            mode: Whether do it for given mode

        Returns:
            The registered function or the decorator
        """
        # if mode == 'jekyll':
        #     from .jekyll.filter_manager import filter_manager as filtermgr
        #     return filtermgr.register(name_or_filter)
        if mode == 'python':
            from .python.filters import filter_manager as filtermgr
            return filtermgr.register(name_or_filter)

        def decorator(filterfunc):
            name = filterfunc.__name__
            name = [name]

            if name_or_filter and name_or_filter is not filterfunc:
                names = name_or_filter
                if isinstance(names, str):
                    names = (nam.strip() for nam in names.split(','))
                name = names
            for nam in name:
                self.__class__.filters[nam] = filterfunc

            return filterfunc

        if callable(name_or_filter):
            return decorator(name_or_filter)

        return decorator

    def unregister(self, name, mode='standard'):
        # type: (str, str) -> Optional[Callable]
        """Unregister a filter

        Args:
            name: The name of the filter to unregister
            mode: Whether do it for given mode

        Returns:
            The unregistered filter or None if name does not exist
        """
        # if mode == 'jekyll':
        #     from .jekyll.filter_manager import filter_manager as filtermgr
        #     return filtermgr.unregister(name)
        if mode == 'python':
            from .python.filters import filter_manager as filtermgr
            return filtermgr.unregister(name)

        try:
            return self.__class__.filters.pop(name)
        except KeyError:
            raise LiquidFilterRegistryException(
                f'No such filter: {name!r}'
            ) from None

# pylint: disable=invalid-name
filter_manager = FilterManager() # type: FilterManager


class EmptyDrop:
    """The EmptyDrop class borrowed from liquid"""
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

def _get_prop(obj, prop):
    """Get the property of the object, allow via getitem"""
    try:
        return obj[prop]
    except (TypeError, KeyError):
        return getattr(obj, prop)

filter_manager.register(str.capitalize)
filter_manager.register(abs)
filter_manager.register(round)
filter_manager.register('concat')(list.__add__)
filter_manager.register('at_least')(max)
filter_manager.register('at_most')(min)
filter_manager.register('downcase')(str.lower)
filter_manager.register('upcase')(str.upper)
filter_manager.register(html.escape)
filter_manager.register(str.lstrip)
filter_manager.register(str.rstrip)
filter_manager.register(str.strip)
filter_manager.register(str.replace)
filter_manager.register('size')(len)

@filter_manager.register
def split(base, sep):
    """Split a string into a list
    If the sep is empty, return the list of characters
    """
    if not sep:
        return list(base)
    return base.split(sep)

@filter_manager.register
def append(base, suffix):
    """Append a suffix to a string"""
    return f"{base}{suffix}"

@filter_manager.register
def prepend(base, prefix):
    """Prepend a prefix to a string"""
    return f"{prefix}{base}"

@filter_manager.register
def times(base, sep):
    """Implementation of * """
    return base * sep

@filter_manager.register
def minus(base, sep):
    """Implementation of - """
    return base - sep

@filter_manager.register
def plus(base, sep):
    """Implementation of + """
    return base + sep

@filter_manager.register
def modulo(base, sep):
    """Implementation of % """
    return base % sep

@filter_manager.register
def ceil(base):
    """Get the ceil of a number"""
    return math.ceil(float(base))

@filter_manager.register
def floor(base):
    """Get the floor of a number"""
    return math.floor(float(base))

@filter_manager.register('date')
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

@filter_manager.register
def default(base, deft):
    """Return the deft value if base is not set.
    Otherwise, return base"""
    if base == 0.0:
        return base
    return base or deft

@filter_manager.register
def divided_by(base, dvdby):
    """Implementation of / or // """
    if isinstance(dvdby, int):
        return base // dvdby
    return base / dvdby

@filter_manager.register
def escape_once(base):
    """Escapse html characters only once of the string"""
    return html.escape(html.unescape(base))

@filter_manager.register
def newline_to_br(base):
    """Replace newline with `<br />`"""
    return base.replace('\n', '<br />')

@filter_manager.register
def remove(base, string):
    """Remove a substring from a string"""
    return base.replace(string, '')

@filter_manager.register
def remove_first(base, string):
    """Remove the first substring from a string"""
    return base.replace(string, '', 1)

@filter_manager.register
def replace_first(base, old, new):
    """Replace the first substring with new string"""
    return base.replace(old, new, 1)

@filter_manager.register
def reverse(base):
    """Get the reversed list"""
    if not base:
        return EmptyDrop()
    return list(reversed(base))

@filter_manager.register
def sort(base):
    """Get the sorted list"""
    if not base:
        return EmptyDrop()
    return list(sorted(base))

@filter_manager.register
def sort_natural(base):
    """Get the sorted list in a case-insensitive manner"""
    if not base:
        return EmptyDrop()
    return list(sorted(base, key=str.casefold))

@filter_manager.register('slice')
def liquid_slice(base, start, length=1):
    """Slice a list"""
    if not base:
        return EmptyDrop()
    if start < 0:
        start = len(base) + start
    return base[start:start+length]

@filter_manager.register
def strip_html(base):
    """Strip html tags from a string"""
    import re
    # use html parser?
    return re.sub(r'<[^>]+>', '', base)

@filter_manager.register
def strip_newlines(base):
    """Strip newlines from a string"""
    return base.replace('\n', '')

@filter_manager.register
def truncate(base, length, ellipsis="..."):
    """Truncate a string"""
    lenbase = len(base)
    if length >= lenbase:
        return base

    return base[:length - len(ellipsis)] + ellipsis

@filter_manager.register
def truncatewords(base, length, ellipsis="..."):
    """Truncate a string by words"""
    # do we need to preserve the whitespaces?
    baselist = base.split()
    lenbase = len(baselist)
    if length >= lenbase:
        return base

    # instead of collapsing them into just a single space?
    return " ".join(baselist[:length]) + ellipsis

@filter_manager.register
def uniq(base):
    """Get the unique elements from a list"""
    if not base:
        return EmptyDrop()
    ret = []
    for bas in base:
        if not bas in ret:
            ret.append(bas)
    return ret

@filter_manager.register
def url_decode(base):
    """Url-decode a string"""
    try:
        from urllib import unquote
    except ImportError:
        from urllib.parse import unquote
    return unquote(base)

@filter_manager.register
def url_encode(base):
    """Url-encode a string"""
    try:
        from urllib import urlencode
    except ImportError:
        from urllib.parse import urlencode
    return urlencode({'': base})[1:]

@filter_manager.register
def where(base, prop, value):
    """Query a list of objects with a given property value"""
    ret = [bas for bas in base if _get_prop(bas, prop) == value]
    return ret or EmptyDrop()

@filter_manager.register('map')
def liquid_map(base, prop):
    """Map a property to a list of objects"""
    return [_get_prop(bas, prop) for bas in base]

@filter_manager.register
def join(base, sep):
    """Join a list by the sep"""
    if isinstance(base, EmptyDrop):
        return ''
    return sep.join(base)

@filter_manager.register
def first(base):
    """Get the first element of the list"""
    if not base:
        return EmptyDrop()
    return base[0]

@filter_manager.register
def last(base):
    """Get the last element of the list"""
    if not base:
        return EmptyDrop()
    return base[-1]

@filter_manager.register
def compact(base):
    """Remove empties from a list"""
    ret = [bas for bas in base if bas]
    return ret or EmptyDrop()
