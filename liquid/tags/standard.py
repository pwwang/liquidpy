"""Provides standard liquid tags"""
from typing import TYPE_CHECKING, List, Union
from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.lexer import TOKEN_BLOCK_END, TOKEN_COLON, TOKEN_STRING

from ..utils import peek_tokens, parse_tag_args
from .manager import TagManager, decode_raw

if TYPE_CHECKING:
    from jinja2.parser import Parser
    from jinja2.lexer import Token


standard_tags = TagManager()


@standard_tags.register(raw=True)  # type: ignore
def comment(token: "Token", parser: "Parser") -> nodes.Node:
    """The comment tag {% comment %} ... {% endcomment %}

    This tag accepts an argument, which is the prefix to be used for each line
    in the body.
    If no prefix provided, the entire body will be ignored (works as the one
    from liquid)

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    return _parse_comment(token, parser, "endcomment")


def _parse_comment(token: "Token", parser: "Parser", end_tag: str) -> nodes.Node:
    if parser.stream.current.type is TOKEN_BLOCK_END:
        # no args provided, ignore whatever
        parser.parse_statements((f"name:{end_tag}",), drop_needle=True)
        return nodes.Output([], lineno=token.lineno)

    args = parser.parse_expression()
    body = parser.parse_statements((f"name:{end_tag}",), drop_needle=True)
    body = decode_raw(body[0].nodes[0].data)  # type: ignore
    body_parts = body.split("\n", 1)
    if not body_parts[0]:
        body = "" if len(body_parts) < 2 else body_parts[1]

    out = [
        nodes.Const(f"{args.value} {line}\n")  # type: ignore
        for line in body.splitlines()
    ]
    return nodes.Output(out, lineno=token.lineno)


@standard_tags.register("inline_comment", raw=True)
def inline_comment(token: "Token", parser: "Parser") -> nodes.Node:
    """The inline_comment tag, which ignores its unparsed body."""
    return _parse_comment(token, parser, "endinline_comment")


@standard_tags.register
def capture(token: "Token", parser: "Parser") -> nodes.Node:
    """The capture tag {% capture var %}...{% endcapture %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    target = parser.parse_assign_target(with_namespace=True)
    filter_node = parser.parse_filter(None)
    body = parser.parse_statements(("name:endcapture",), drop_needle=True)
    return nodes.AssignBlock(target, filter_node, body, lineno=token.lineno)


@standard_tags.register
def assign(token: "Token", parser: "Parser") -> nodes.Node:
    """The assign tag {% assign x = ... %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    target = parser.parse_assign_target(with_namespace=True)
    parser.stream.expect("assign")
    expr = parser.parse_tuple()
    return nodes.Assign(target, expr, lineno=token.lineno)


@standard_tags.register
def unless(token: "Token", parser: "Parser") -> nodes.Node:
    """The unless tag {% unless ... %} ... {% endunless %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    node = result = nodes.If(lineno=token.lineno)
    while True:
        node.test = nodes.Not(
            parser.parse_tuple(with_condexpr=False),
            lineno=token.lineno,
        )
        node.body = parser.parse_statements(
            ("name:elif", "name:elsif", "name:else", "name:endunless")
        )
        node.elif_ = []
        node.else_ = []
        token = next(parser.stream)
        if token.test_any("name:elif", "name:elsif"):
            node = nodes.If(lineno=parser.stream.current.lineno)
            result.elif_.append(node)
            continue
        if token.test("name:else"):
            result.else_ = parser.parse_statements(
                ("name:endunless",), drop_needle=True
            )
        break
    return result


@standard_tags.register
def case(token: "Token", parser: "Parser") -> nodes.Node:
    """The case-when tag {% case x %}{% when y %} ... {% endcase %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    lhs = parser.parse_tuple(with_condexpr=False)
    # %}
    if not parser.stream.skip_if("block_end"):
        raise TemplateSyntaxError(  # pragma: no cover
            "Expected 'end of statement block'",
            token.lineno,
        )
    token = next(parser.stream)
    if token.type == "data":
        if token.value.strip():
            raise TemplateSyntaxError(
                "Expected nothing or whitespaces between case and when, "
                f"but got {token}",
                token.lineno,
            )
        token = next(parser.stream)

    if token.type != "block_begin":
        raise TemplateSyntaxError(
            "Expected 'begin of statement block', " f"but got {token}",
            token.lineno,
        )

    token = parser.stream.expect("name:when")
    node = result = nodes.If(lineno=token.lineno)
    while True:
        when_values = parser.parse_tuple(with_condexpr=False)
        when_values = (
            when_values.items if isinstance(when_values, nodes.Tuple)
            else [when_values]
        )
        tests = [
            nodes.Test(lhs, "liquid_eq", [value], [], None, None)
            for value in when_values
        ]
        test = tests[0]
        for value_test in tests[1:]:
            test = nodes.Or(test, value_test)
        node.test = test
        node.body = parser.parse_statements(
            ("name:when", "name:else", "name:endcase")
        )
        node.elif_ = []
        node.else_ = []
        token = next(parser.stream)
        if token.test("name:when"):
            node = nodes.If(lineno=parser.stream.current.lineno)
            result.elif_.append(node)
            continue
        if token.test("name:else"):
            result.else_ = parser.parse_statements(
                ("name:endcase",), drop_needle=True
            )
        break
    return result


@standard_tags.register
def tablerow(
    token: "Token", parser: "Parser"
) -> Union[nodes.Node, List[nodes.Node]]:
    """The tablerow tag {% tablerow ... %} ... {% endtablerow %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    target = parser.parse_assign_target(extra_end_rules=("name:in", ))
    parser.stream.expect("name:in")
    iter_ = parser.parse_tuple(
        with_condexpr=False,
        extra_end_rules=("name:cols", "name:limit", "name:offset"),
    )

    cols = parse_tag_args(parser.stream, "cols", token.lineno)
    limit = parse_tag_args(parser.stream, "limit", token.lineno)
    offset = parse_tag_args(parser.stream, "offset", token.lineno)

    if limit and offset:
        limit = nodes.Add(offset, limit)
    if limit or offset:
        iter_ = nodes.Getitem(iter_, nodes.Slice(offset, limit, None), "load")

    if cols:
        slice_start = nodes.Mul(nodes.Name("_tablerow_i", "load"), cols)
        inner_iter = nodes.Getitem(
            iter_,
            nodes.Slice(
                slice_start,
                nodes.Add(slice_start, cols),
                None,
            ),
            "load",
        )
    else:
        inner_iter: nodes.Getitem = iter_  # type: ignore

    inner_body = [
        nodes.Output(
            [
                nodes.Const('<td class="col'),
                nodes.Getattr(nodes.Name("loop", "load"), "index", "load"),
                nodes.Const('">'),
            ]
        ),
        *parser.parse_statements(("name:endtablerow",), drop_needle=True),
        nodes.Output([nodes.Const("</td>")]),
    ]
    broken = f"_tablerow_broken_{token.lineno}_{id(token)}" if cols else None
    _close_tablerow_breaks(inner_body, broken)
    tr_begin = nodes.Output(
        [
            nodes.Const('<tr class="row'),
            nodes.CondExpr(
                nodes.Name("loop", "load"),
                nodes.Getattr(nodes.Name("loop", "load"), "index", "load"),
                nodes.Const(1),
            ),
            nodes.Const('">'),
        ]
    )
    tr_end = nodes.Output([nodes.Const("</tr>")])
    inner_loop = nodes.For(
        target, inner_iter, inner_body, [], None, False, lineno=token.lineno
    )
    if not cols:
        return [tr_begin, inner_loop, tr_end]

    # (iter_ | length) / cols
    iter_length = nodes.Div(
        nodes.Filter(iter_, "length", [], [], None, None),
        cols,
    )  # float
    # int(iter_length)
    iter_length_int = nodes.Filter(iter_length, "int", [], [], None, None)

    # implement ceil, as jinja's ceil is implemented as round(..., "ceil")
    # while liquid has a ceil filter
    # iter_length_int if iter_length == iter_length_int
    # else iter_length_int + 1
    iter_length = nodes.CondExpr(
        nodes.Compare(iter_length, [nodes.Operand("eq", iter_length_int)]),
        iter_length_int,
        nodes.Add(iter_length_int, nodes.Const(1)),
    )

    return [
        nodes.Assign(
            nodes.Name(broken, "store"),
            nodes.Call(
                nodes.Name("namespace", "load"),
                [],
                [nodes.Keyword("broken", nodes.Const(False))],
                None,
                None,
            ),
        ),
        nodes.For(
            nodes.Name("_tablerow_i", "store"),
            nodes.Call(nodes.Name("range", "load"), [iter_length], [], None, None),
            [
                nodes.If(
                    nodes.Not(
                        nodes.Getattr(nodes.Name(broken, "load"), "broken", "load")
                    ),
                    [tr_begin, inner_loop, tr_end],
                    [],
                    [],
                    None,
                    lineno=token.lineno,
                )
            ],
            [],
            None,
            False,
            lineno=token.lineno,
        ),
    ]


def _close_tablerow_breaks(body, broken=None):
    """Close the current cell before a break exits the tablerow loop."""
    index = 0
    while index < len(body):
        node = body[index]
        if isinstance(node, nodes.Break):
            close = nodes.Output(
                [nodes.Const("</td>")],
                lineno=node.lineno,
            )
            if broken is not None:
                body[index:index] = [
                    close,
                    nodes.Assign(
                        nodes.NSRef(broken, "broken"),
                        nodes.Const(True),
                    ),
                ]
                index += 3
            else:
                body.insert(index, close)
                index += 2
            continue
        if isinstance(node, nodes.If):
            _close_tablerow_breaks(node.body, broken)
            for branch in node.elif_:
                _close_tablerow_breaks(branch.body, broken)
            _close_tablerow_breaks(node.else_, broken)
        index += 1


@standard_tags.register
def increment(token: "Token", parser: "Parser") -> List[nodes.Node]:
    """The increment tag {% increment x %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    variable = parser.stream.expect("name")
    varname = f"_liquid_xcrement_{variable.value}"
    varnode = nodes.Name(varname, "load")

    return [
        nodes.Assign(
            nodes.Name(varname, "store"),
            nodes.CondExpr(
                nodes.Test(varnode, "defined", [], [], None, None),
                nodes.Add(varnode, nodes.Const(1)),
                nodes.Const(0),
            ),
            lineno=token.lineno,
        ),
        nodes.Output([varnode], lineno=token.lineno),
    ]


@standard_tags.register
def decrement(token: "Token", parser: "Parser") -> List[nodes.Node]:
    """The decrement tag {% decrement x %}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    variable = parser.stream.expect("name")
    varname = f"_liquid_xcrement_{variable.value}"
    varnode = nodes.Name(varname, "load")

    return [
        nodes.Assign(
            nodes.Name(varname, "store"),
            nodes.CondExpr(
                nodes.Test(varnode, "defined", [], [], None, None),
                nodes.Sub(varnode, nodes.Const(1)),
                nodes.Const(-1),
            ),
            lineno=token.lineno,
        ),
        nodes.Output([varnode], lineno=token.lineno),
    ]


@standard_tags.register
def cycle(token: "Token", parser: "Parser") -> nodes.Node:
    """The cycle tag {% cycle ... %}

    With name: {% cycle "name": "one", "two", "three" %}
    Without: {% cycle "one", "two", "three" %}

    Turn these to
    {{ loop.liquid_cycle("one", "two", "three", name=...) }}

    Args:
        token: The token matches tag name
        parser: The parser

    Returns:
        The parsed node
    """
    tokens_ahead = peek_tokens(parser.stream, 2)
    if (
        len(tokens_ahead) == 2
        and tokens_ahead[0].type is TOKEN_STRING
        and tokens_ahead[1].type is TOKEN_COLON
    ):
        parser.stream.skip(2)
        cycler_name = tokens_ahead[0].value
    else:
        cycler_name = ""

    args = parser.parse_tuple(with_condexpr=False, simplified=True)
    return nodes.Output(
        [
            nodes.Call(
                nodes.Getattr(
                    nodes.Name("loop", "load"), "liquid_cycle", "load"
                ),
                args.items if isinstance(args, nodes.Tuple) else [args],
                [nodes.Keyword("name", nodes.Const(cycler_name))],
                None,
                None,
                lineno=token.lineno,
            )
        ]
    )
