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

@filter_manager.register
def render(base, **envs):
    """Render a template in python mode"""
    import sys
    from ..liquid import LiquidPython
    from ..config import LIQUID_FILTERS_ENVNAME
    frame = sys._getframe(2)
    local_vars = frame.f_locals['local_vars']
    global_vars = frame.f_locals['global_vars'].copy()
    global_vars.update(local_vars)
    global_vars.update(envs)
    del global_vars[LIQUID_FILTERS_ENVNAME]
    return LiquidPython(base).render(**global_vars)
