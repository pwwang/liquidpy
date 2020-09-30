"""Management for filters in extended mode"""
from ..filters import FilterManager as FilterManagerStandard, EmptyDrop

class FilterManager(FilterManagerStandard):
    """A manager for filters in extended mode"""
    INSTANCE = None
    filters = FilterManagerStandard.filters.copy() # type: Dict[str, Callable]

# pylint: disable=invalid-name
filter_manager = FilterManager()

def _no_emptydrop(name):
    """No emptydrop of the filters"""
    original_filter = filter_manager.filters[name]
    def new_filter(*args, **kwargs):
        ret = original_filter(*args, **kwargs)
        if isinstance(ret, EmptyDrop):
            return args[0]
        return ret
    filter_manager.register(name)(new_filter)

for filter_name in ('reverse', 'sort', 'sort_natural', 'slice',
                    'uniq', 'where', 'first', 'last', 'compact'):
    _no_emptydrop(filter_name)

@filter_manager.register
def getitem(base, index):
    """Get an item from the base value"""
    return base[index]
