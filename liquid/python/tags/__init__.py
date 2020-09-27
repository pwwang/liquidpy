"""Tags related definitions for python mode"""
import pkgutil
from .inherited import Tag, tag_manager

# load all builtin tags
for _, modname, _ in pkgutil.walk_packages(__path__):
    if modname.startswith('tag_'):
        __import__(f'{__name__}.{modname}')
