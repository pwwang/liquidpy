"""Extension for shopify mode"""
from ..tags.shopify import shopify_tags
from .standard import LiquidStandardExtension


class LiquidJekyllExtension(LiquidStandardExtension):

    tag_manager = shopify_tags
