"""Management for filters in extended mode"""
from ..filters import FilterManager as FilterManagerStandard

class FilterManager(FilterManagerStandard):
    """A manager for filters in extended mode"""
    INSTANCE = None

    # type: Dict[str, Callable]
    filters = FilterManagerStandard.filters.copy()

# pylint: disable=invalid-name
filter_manager = FilterManager()
