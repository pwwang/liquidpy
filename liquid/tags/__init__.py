"""All stuff about liquidpy tags"""
import pkgutil

from .manager import tag_manager
from .tag import Tag

# load all builtin tags
for _, modname, _ in pkgutil.walk_packages(__path__):
    if modname.startswith('tag_'):
        __import__(f'{__name__}.{modname}')
