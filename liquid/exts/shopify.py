"""Extension for shopify mode"""
from ..tags.shopify import shopify_tags
from .standard import LiquidStandardExtension


class LiquidShopifyExtension(LiquidStandardExtension):
    """Extension for jekyll mode"""
    tag_manager = shopify_tags
