"""Extension for shopify mode"""
import re
from base64 import b64encode
from collections.abc import Mapping

from jinja2 import nodes
from jinja2.compiler import CodeGenerator
from jinja2 import Undefined
from jinja2.lexer import TOKEN_NAME, Token

from ..tags.shopify import shopify_tags
from ..filters.shopify import (
    _ShopifyDrop,
    blank,
    empty,
    liquid_contains,
    liquid_equal,
)
from .ext import ENCODING_ID
from .standard import LiquidStandardExtension


_COMMENT_TAG = re.compile(
    r"{%[-+]?\s*(end)?comment\b.*?[-+]?%}",
    re.DOTALL,
)
CARRIAGE_RETURN = "\ue000"


class ShopifyHash(dict):
    def __iter__(self):
        return iter(self.items())


def shopify_context(value):
    if isinstance(value, Mapping) and not isinstance(value, ShopifyHash):
        return ShopifyHash({key: shopify_context(item) for key, item in value.items()})
    if isinstance(value, list):
        return [shopify_context(item) for item in value]
    if isinstance(value, tuple):
        return tuple(shopify_context(item) for item in value)
    return value


class ShopifyCodeGenerator(CodeGenerator):
    def visit_Assign(self, node, frame):
        super().visit_Assign(node, frame)
        if (
            not (frame.loop_frame or frame.buffer is not None)
            or not isinstance(node.target, nodes.Name)
        ):
            return

        name = node.target.name
        ref = frame.symbols.ref(name)
        symbols = frame.symbols.parent
        while symbols is not None:
            if symbols.find_ref(name) is not None:
                self.writeline(f"{symbols.find_ref(name)} = {ref}")
            symbols = symbols.parent

    def visit_If(self, node, frame):
        branches = [node, *node.elif_]
        for branch in branches:
            if _whitespace_only(branch.body):
                branch.body = []
            if _whitespace_only(branch.else_):
                branch.else_ = []
        super().visit_If(node, frame)


def _whitespace_only(body):
    for node in body:
        if isinstance(node, nodes.Output):
            if any(
                not (
                    isinstance(item, nodes.TemplateData)
                    and not item.data.strip()
                    or isinstance(item, nodes.Const)
                    and isinstance(item.value, str)
                    and not item.value.strip()
                )
                for item in node.nodes
            ):
                return False
        elif isinstance(node, nodes.If):
            if not all(
                _whitespace_only(branch.body + branch.else_)
                for branch in [node, *node.elif_]
            ):
                return False
        else:
            return False
    return True


class LiquidShopifyExtension(LiquidStandardExtension):
    """Extension for jekyll mode"""
    tag_manager = shopify_tags

    def __init__(self, environment):
        super().__init__(environment)
        environment.code_generator_class = ShopifyCodeGenerator
        environment.tests["contains"] = liquid_contains
        environment.tests["liquid_eq"] = liquid_equal
        environment.tests.update(
            {
                "liquid_lt": lambda left, right: _liquid_relation(left, right, "lt"),
                "liquid_lte": lambda left, right: _liquid_relation(left, right, "le"),
                "liquid_gt": lambda left, right: _liquid_relation(left, right, "gt"),
                "liquid_gte": lambda left, right: _liquid_relation(left, right, "ge"),
            }
        )
        environment.globals.update({"blank": blank, "empty": empty})
        previous_finalize = environment.finalize

        def finalize(value):
            if value is None:
                return ""
            if isinstance(value, (list, tuple, dict, range)) or hasattr(
                value, "__next__"
            ):
                return ""
            return previous_finalize(value) if previous_finalize else value

        environment.finalize = finalize

    def preprocess(self, source, name, filename):
        source = re.sub(r"{%[-+]?\s*#.*?%}", "", source, flags=re.DOTALL)
        nested_comments = []
        depth = 0
        for match in _COMMENT_TAG.finditer(source):
            if match.group(1):
                if depth > 1:
                    nested_comments.append((match.start(), match.end()))
                depth = max(0, depth - 1)
            else:
                if depth:
                    nested_comments.append((match.start(), match.end()))
                depth += 1
        for start, end in reversed(nested_comments):
            tag = source[start:end]
            encoded = (
                f"$${ENCODING_ID}${b64encode(tag.encode()).decode()}$$"
            )
            source = source[:start] + encoded + source[end:]
        source = source.replace("\r", CARRIAGE_RETURN)
        source = re.sub(r"[\s\ue000]*({%-|{{-)", r"\1", source)
        source = re.sub(r"(-%}|-}})[\s\ue000]*", r"\1", source)
        return super().preprocess(source, name, filename)

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
            elif token.type == "lt" and stream.current.type == "gt":
                stream.skip()
                yield Token(token.lineno, TOKEN_NAME, "is")
                yield Token(token.lineno, TOKEN_NAME, "not")
                yield Token(token.lineno, TOKEN_NAME, "liquid_eq")
            elif token.type in ("lt", "lteq", "gt", "gteq"):
                tests = {
                    "lt": "liquid_lt",
                    "lteq": "liquid_lte",
                    "gt": "liquid_gt",
                    "gteq": "liquid_gte",
                }
                yield Token(token.lineno, TOKEN_NAME, "is")
                yield Token(token.lineno, TOKEN_NAME, tests[token.type])
            else:
                yield token


def _liquid_relation(left, right, operator):
    if left is None or right is None or isinstance(left, Undefined) or isinstance(
        right, Undefined
    ):
        return False
    if isinstance(left, _ShopifyDrop) or isinstance(right, _ShopifyDrop):
        return False
    if isinstance(left, bool) != isinstance(right, bool):
        return False
    try:
        if operator == "lt":
            return left < right
        if operator == "le":
            return left <= right
        if operator == "gt":
            return left > right
        return left >= right
    except TypeError:
        return False
