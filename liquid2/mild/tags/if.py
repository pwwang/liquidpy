import ast
from lark import v_args
from ...common.tagmgr import register_tag
from ...common.tagparser import (
    Tag, TagTransformer, TagParsedVar, TagParsedConst,
    TagParsedOpComparison,
    TagParsedGetItem,
    TagParsedGetAttr
)

@v_args(inline=True)
class TransformerIf(TagTransformer):

    def var(self, varname):
        return TagParsedVar(varname)

    def expr(self, exprstr):
        return exprstr

    def atom(self, atomnode):
        return atomnode

    def number(self, numstr):
        return TagParsedConst(ast.literal_eval(numstr))

    def op_comparison(self, left, op, right):
        return TagParsedOpComparison(left, op, right)

    def getitem(self, obj, subscript):
        return TagParsedGetItem(obj, subscript)

    def getattr(self, obj, subscript):
        return TagParsedGetAttr(obj, subscript)

    def string(self, quoted_string):
        return TagParsedConst(quoted_string[1:-1]
                              .replace('\\\'', '\'')
                              .replace('\\"', '"'))
    def nil(self):
        return TagParsedConst(None)

    def true(self):
        return TagParsedConst(True)

    def false(self):
        return TagParsedConst(False)

    contains = op_comparison
    logical_or = op_comparison
    logical_and = op_comparison

class TagIf(Tag):
    VOID = False

    SYNTAX = r"""
    start: expr

    // we have to use earley to make this priority work
    ?expr: "(" expr ")"
        | logical_or
        | logical_and
        | op_comparison
        | contains
        | expr "[" expr "]"    -> getitem
        | expr "." ATTRNAME    -> getattr
        | atom

    !logical_or: expr "or" expr
    !logical_and: expr "and" expr
    op_comparison: expr OP expr
    !contains: expr "contains" expr

    ?atom: number | string
        | "nil"   -> nil
        | "true"  -> true
        | "false" -> false
        | VAR     -> var

    number: DEC_NUMBER | HEX_NUMBER | BIN_NUMBER | OCT_NUMBER | FLOAT_NUMBER
    string: STRING

    OP: "<>"|"=="|">="|"<="|"!="|"<"|">"
    STRING: (ESCAPED_STRING | "'" _STRING_ESC_INNER "'")
    ATTRNAME: /[A-Za-z_][\w_\-]*/
    DEC_NUMBER: /0|[1-9]\d*/i
    HEX_NUMBER: /0x[\da-f]*/i
    OCT_NUMBER: /0o[0-7]*/i
    BIN_NUMBER : /0b[0-1]*/i
    FLOAT_NUMBER: /((\d+\.\d*|\.\d+)(e[-+]?\d+)?|\d+(e[-+]?\d+))/i

    %import common.CNAME -> VAR
    %import common (ESCAPED_STRING, _STRING_ESC_INNER, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerIf

    def render(self, envs):
        condition = self.parse()
        condition = condition.render(envs)
        if condition:
            return self._children_rendered(envs), envs
        return [], envs

register_tag('if', TagIf)
