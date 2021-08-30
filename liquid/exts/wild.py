"""Provides extension for wild mode"""

from ..tags.wild import wild_tags

from .ext import LiquidExtension


class LiquidWildExtension(LiquidExtension):
    """Extension for wild mode"""
    tag_manager = wild_tags
