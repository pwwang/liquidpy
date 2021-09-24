"""Patch a couple of jinja functions to implement some features
that are impossible or too complex to be implemented by extensions

Including
1. Patching Parser.parse to allow 'elsif' in addition to 'elif'
2. Patching LoopContext to allow rindex and rindex0
3. Adding liquid_cycle method to LoopContext to allow cycle to have a name
4. Patching Parser.parse_for to allow arguments for tag 'for'
"""
from typing import Any
from jinja2 import nodes
from jinja2.parser import Parser
from jinja2.runtime import LoopContext

from .utils import parse_tag_args


# patching Parser.parse_if to allow elsif in addition to elif
# -----------------------------------------------------------
def parse_if(self) -> nodes.Node:
    node = result = nodes.If(lineno=self.stream.expect("name:if").lineno)
    while True:
        node.test = self.parse_tuple(with_condexpr=False)
        node.body = self.parse_statements(
            ("name:elif", "name:elsif", "name:else", "name:endif")
        )
        node.elif_ = []
        node.else_ = []
        token = next(self.stream)
        if token.test_any("name:elif", "name:elsif"):
            node = nodes.If(lineno=self.stream.current.lineno)
            result.elif_.append(node)
            continue
        elif token.test("name:else"):
            result.else_ = self.parse_statements(
                ("name:endif",), drop_needle=True
            )
        break
    return result


jinja_nodes_if_fields = nodes.If.fields
jinja_parse_if = Parser.parse_if


# patching LoopContext to allow rindex and rindex0
# Also add liquid_cycle method to allow cycle to have a name
# -----------------------------------------------------------
def cycle(self, *args: Any, name: Any = None) -> Any:
    if not hasattr(self, "_liquid_cyclers"):
        setattr(self, "_liquid_cyclers", {})
    cyclers = self._liquid_cyclers
    if name not in cyclers:
        cyclers[name] = [args, -1]
    cycler = cyclers[name]
    cycler[1] += 1
    return cycler[0][cycler[1] % len(cycler[0])]


# patching Parser.parse_for to allow arguments
# -----------------------------------------------------------
def parse_for(self) -> nodes.Node:
    lineno = self.stream.expect("name:for").lineno
    target = self.parse_assign_target(extra_end_rules=("name:in",))
    self.stream.expect("name:in")
    iter = self.parse_tuple(
        with_condexpr=False,
        extra_end_rules=(
            "name:recursive",
            "name:reversed",
            "name:limit",
            "name:offset",
        ),
    )
    reverse = self.stream.skip_if("name:reversed")
    limit = parse_tag_args(self.stream, "limit", lineno)
    offset = parse_tag_args(self.stream, "offset", lineno)
    if limit and offset:
        limit = nodes.Add(offset, limit)
    if limit or offset:
        iter = nodes.Getitem(iter, nodes.Slice(offset, limit, None), "load")
    if reverse:
        iter = nodes.Filter(iter, "reverse", [], [], None, None)

    test = None
    if self.stream.skip_if("name:if"):
        test = self.parse_expression()
    recursive = self.stream.skip_if("name:recursive")
    body = self.parse_statements(("name:endfor", "name:else"))
    if next(self.stream).value == "endfor":
        else_ = []
    else:
        else_ = self.parse_statements(("name:endfor",), drop_needle=True)
    return nodes.For(target, iter, body, else_, test, recursive, lineno=lineno)


jinja_parse_for = Parser.parse_for


def patch_jinja():
    """Monkey-patch jinja"""
    nodes.If.fields = jinja_nodes_if_fields + ("elsif",)
    nodes.If.elsif = None
    Parser.parse_if = parse_if

    LoopContext.rindex = LoopContext.revindex
    LoopContext.rindex0 = LoopContext.revindex0
    LoopContext.liquid_cycle = cycle

    Parser.parse_for = parse_for


def unpatch_jinja():
    """Restore the patches to jinja"""
    nodes.If.fields = jinja_nodes_if_fields
    del nodes.If.elsif

    Parser.parse_if = jinja_parse_if
    del LoopContext.rindex
    del LoopContext.rindex0
    del LoopContext.liquid_cycle

    Parser.parse_for = jinja_parse_for
