"""A manager for filters"""
from .exceptions import FilterRegistryException

LIQUID_FILTERS = {}

def register_filter(name_or_filter):
    """Decorator to register a filter"""
    if callable(name_or_filter):
        name, liqfilter = name_or_filter.__name__, name_or_filter
        LIQUID_FILTERS[name] = liqfilter

    else:
        names = name_or_filter
        if not isinstance(names (tuple, list)):
            names = [names]

        def decorator(func):
            for name in names:
                LIQUID_FILTERS[name] = func
            # reuse the filter somewhere else
            # (other than in the template)?
            return func
        return decorator

def unregister_filter(filtername):
    """Unregister a filter from the registry"""
    del LIQUID_FILTERS[filtername]

def enable_filter(filtername):
    """Enable a disabled filter"""
    key = f"disabled::{filtername}"
    if key not in LIQUID_FILTERS:
        raise FilterRegistryException(
            f"Filter is unregisted or already enabled: {filtername}"
        )
    LIQUID_FILTERS[filtername] = LIQUID_FILTERS.pop(key)

def disable_filter(filtername):
    """Disable a filter"""
    key = f"disabled::{filtername}"
    if key in LIQUID_FILTERS or filtername not in LIQUID_FILTERS:
        raise FilterRegistryException(
            f"Filter is unregisted or already disabled: {filtername}"
        )
    LIQUID_FILTERS[key] = LIQUID_FILTERS.pop(filtername)

