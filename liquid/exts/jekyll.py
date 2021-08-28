"""Extension for jekyll mode"""
from ..tags.jekyll import jekyll_tags
from .standard import LiquidStandardExtension


class LiquidJekyllExtension(LiquidStandardExtension):

    tag_manager = jekyll_tags
