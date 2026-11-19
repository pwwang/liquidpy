"""Extension for shopify mode"""
from jinja2 import nodes
from jinja2.compiler import CodeGenerator
from jinja2.lexer import TOKEN_NAME, Token

from ..tags.shopify import shopify_tags
from ..filters.shopify import blank, empty, liquid_contains, liquid_equal
from .standard import LiquidStandardExtension


class ShopifyCodeGenerator(CodeGenerator):
    def visit_Assign(self, node, frame):
        super().visit_Assign(node, frame)
        if not frame.loop_frame or not isinstance(node.target, nodes.Name):
            return

        name = node.target.name
        ref = frame.symbols.ref(name)
        symbols = frame.symbols.parent
        while symbols is not None:
            if symbols.find_ref(name) is not None:
                self.writeline(f"{symbols.find_ref(name)} = {ref}")
            symbols = symbols.parent


class LiquidShopifyExtension(LiquidStandardExtension):
    """Extension for jekyll mode"""
    tag_manager = shopify_tags

    def __init__(self, environment):
        super().__init__(environment)
        environment.code_generator_class = ShopifyCodeGenerator
        environment.tests["contains"] = liquid_contains
        environment.tests["liquid_eq"] = liquid_equal
        environment.globals.update({"blank": blank, "empty": empty})

    def filter_stream(self, stream):
        for token in super().filter_stream(stream):
            if token.type in ("eq", "ne"):
                if token.type == "eq":
                    yield Token(token.lineno, TOKEN_NAME, "is")
                    yield Token(token.lineno, TOKEN_NAME, "liquid_eq")
                else:
                    yield Token(token.lineno, TOKEN_NAME, "is")
                    yield Token(token.lineno, TOKEN_NAME, "not")
                    yield Token(token.lineno, TOKEN_NAME, "liquid_eq")
            elif (
                token.type == "lt"
                and stream.current.type == "gt"
            ):
                stream.skip()
                yield Token(token.lineno, TOKEN_NAME, "is")
                yield Token(token.lineno, TOKEN_NAME, "not")
                yield Token(token.lineno, TOKEN_NAME, "liquid_eq")
            else:
                yield token
