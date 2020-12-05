"""A port of liquid template engine in python"""
from .liquid import Liquid
from .filters import filter_manager
from .tags import tag_manager, Tag
from .exceptions import (
    LiquidException,
    LiquidTagRegistryException,
    LiquidFilterRegistryException,
    LiquidNameError,
    LiquidSyntaxError,
    LiquidRenderError,
)

# python mode
from .liquid import LiquidPython
from .python.tags import tag_manager as tag_manager_python, Tag as TagPython
from .python.filters import filter_manager as filter_manager_python

__version__ = '0.6.3'
