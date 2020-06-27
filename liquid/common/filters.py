from ..filtermgr import register_filter

@register_filter
def append(base, suffix):
    return f"{base}{suffix}"

@register_filter
def prepend(base, prefix):
    return f"{prefix}{base}"

@register_filter
def capitalize(base):
    return base.capitalize()
