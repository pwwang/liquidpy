from ..filtermgr import register_filter

@register_filter
def append(base, suffix):
    return f"{base}{suffix}"
