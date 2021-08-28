"""Provides some wild filters"""

try:
    from jinja2 import pass_environment
except ImportError:
    from jinja2 import environmentfilter as pass_environment

from .manager import FilterManager

wild_filter_manager = FilterManager()
