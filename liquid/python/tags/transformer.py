"""The segments and transformer for liquidpy in python mode"""
from functools import partialmethod
from lark import v_args, Token
from ...config import LIQUID_FILTERS_ENVNAME
from ...tags.transformer import (
    render_segment,
    TagSegment,
    TagSegmentComparison,
    TagSegmentArguments,
    TagTransformer as TagTransformerStandard
)
from ...utils import NOTHING

class TagSegmentIfelse(TagSegment):
    """The ternary operation in python: `A if cond else B`"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        # pylint: disable=unused-argument
        """Render the segment with the given envs"""
        cond = render_segment(self.data[1], local_vars, global_vars)
        if cond:
            return render_segment(self.data[0], local_vars, global_vars)
        return render_segment(self.data[2], local_vars, global_vars)

class TagSegmentOr(TagSegment):
    """Or statement in python"""
    def render(self, local_vars, global_vars):
        for data in self.data:
            data = render_segment(data, local_vars, global_vars)
            if data:
                return data
        return False

class TagSegmentAnd(TagSegment):
    """And statement in python"""
    def render(self, local_vars, global_vars):
        lastdata = None
        for data in self.data:
            data = render_segment(data, local_vars, global_vars)
            if not data:
                return data
            lastdata = data
        return lastdata

class TagSegmentNot(TagSegment):
    """Not statement in python"""
    def render(self, local_vars, global_vars):
        return not render_segment(self.data[0], local_vars, global_vars)

class TagSegmentGetAttr(TagSegment):
    """Getattr operation in python"""
    def render(self, local_vars, global_vars):
        obj = render_segment(self.data[0], local_vars, global_vars)
        try:
            return getattr(obj, self.data[1])
        except AttributeError as exc:
            try:
                return obj[self.data[1]]
            except KeyError:
                raise exc from exc

class TagSegmentGetItem(TagSegment):
    """Getitem operation in python"""

    def render(self, local_vars, global_vars):
        return render_segment(self.data[0], local_vars, global_vars)[
            render_segment(self.data[1], local_vars, global_vars)
        ]

class TagSegmentExpr(TagSegment):
    """Expressions in python"""
    def render(self, local_vars, global_vars):
        sign = self.data[0]
        ret = render_segment(self.data[1], local_vars, global_vars)
        for data in self.data[2:]:
            data = render_segment(data, local_vars, global_vars)
            if sign == '|':
                ret |= data
            elif sign == '^':
                ret ^= data
            elif sign == '&':
                ret &= data
            elif sign == '<<':
                ret <<= data
            elif sign == '>>':
                ret >>= data
            elif sign == '+':
                ret += data
            elif sign == '-':
                ret -= data
            elif sign == '*':
                ret *= data
            elif sign == '@': # pragma: no cover
                ret @= data
            elif sign == '/':
                ret /= data
            elif sign == '%':
                ret %= data
            elif sign == '//':
                ret //= data

        return ret

class TagSegmentPower(TagSegment):
    """Power expression in python"""
    def render(self, local_vars, global_vars):
        data1 = render_segment(self.data[0], local_vars, global_vars)
        data2 = render_segment(self.data[1], local_vars, global_vars)
        return data1 ** data2

class TagSegmentFactor(TagSegment):
    """Factor expression in python"""

    def render(self, local_vars, global_vars):
        factor_op, factor = self.data
        factor = render_segment(factor, local_vars, global_vars)
        if factor_op == '-':
            return -factor
        if factor_op == '~':
            return ~factor
        return factor

class TagSegmentFuncCall(TagSegment):
    """Function call in python

    We simplified the function call in python, no start arguments (*args) nor
    keyword arguments (**kwargs) allowed.
    """

    def render(self, local_vars, global_vars):
        func = render_segment(self.data[0], local_vars, global_vars)
        if self.data[1] is None:
            return func()
        args, kwargs = render_segment(self.data[1], local_vars, global_vars)
        return func(*args, **kwargs)

class TagSegmentTuple(TagSegment):
    """Tuple literals in python"""
    def render(self, local_vars, global_vars):
        if not self.data or self.data[0] is NOTHING:
            return ()
        return tuple(render_segment(data, local_vars, global_vars)
                     for data in self.data[0])

class TagSegmentList(TagSegment):
    """List literals in python"""
    def render(self, local_vars, global_vars):
        if not self.data or self.data[0] is NOTHING:
            return []
        return list(render_segment(data, local_vars, global_vars)
                    for data in self.data[0])

class TagSegmentSet(TagSegment):
    """Set literals in python"""
    def render(self, local_vars, global_vars):
        return set(render_segment(data, local_vars, global_vars)
                   for data in self.data)

class TagSegmentDict(TagSegment):
    """Dict literals in python"""
    def render(self, local_vars, global_vars):
        return {
            render_segment(key, local_vars, global_vars):
            render_segment(val, local_vars, global_vars)
            for key, val in self.data
        }

class TagSegmentSlice(TagSegment):
    """Slice objects in python"""
    def render(self, local_vars, global_vars):
        if len(self.data) == 1:
            return render_segment(self.data[0], local_vars, global_vars)
        return slice(*(render_segment(data, local_vars, global_vars)
                       for data in self.data))

class TagSegmentOutput(TagSegment):
    """Output inside {{ ... }}"""
    def render(self, local_vars, global_vars):
        """Render the output segment"""
        base = render_segment(self.data[0], local_vars, global_vars)
        if len(self) == 1:
            return base

        # filter_name is Token
        for filter_name, filter_arg in self.data[1:]:
            if filter_arg is None:
                filter_args, filter_kwargs = (), {}
            else:
                filter_args, filter_kwargs = filter_arg.render(
                    local_vars, global_vars
                )
            filtname = str(filter_name)

            filter_func = global_vars[LIQUID_FILTERS_ENVNAME].get(
                filtname, global_vars.get(filtname, NOTHING)
            )

            if filter_func is NOTHING:
                error = KeyError(f'No such filter: {filtname!r}')
                error.lineno = filter_name.line
                error.colno = filter_name.column
                raise error

            base = filter_func(base, *filter_args, **filter_kwargs)

        return base

@v_args(inline=True)
class TagTransformer(TagTransformerStandard):
    """Transformer for python grammar"""
    def test(self, value, cond=None, false_value=None):
        if cond is None and false_value is None:
            return value
        return TagSegmentIfelse(value, cond, false_value)

    def comparison(self, expr, *op_and_exprs):
        ret = expr
        op = ''
        i = 0
        while i < len(op_and_exprs):
            if isinstance(op_and_exprs[i], Token):
                op += op_and_exprs[i].value
            if isinstance(op_and_exprs[i+1], Token):
                op += op_and_exprs[i+1].value
                expr2 = op_and_exprs[i+2]
                i += 3
            else:
                expr2 = op_and_exprs[i+1]
                i += 2

            ret = TagSegmentComparison(ret, op, expr2)
            op = ''
        return ret


    def term(self, one, *more):
        if not more:
            return one
        return TagSegmentExpr(
            more[0], one, *(mor for i, mor in enumerate(more) if i % 2)
        )

    def factor(self, factor_op_or_power, factor=None):
        if factor is None:
            return factor_op_or_power

        return TagSegmentFactor(factor_op_or_power, factor)

    def power(self, atom_expr, factor=None):
        if factor is None:
            return atom_expr
        return TagSegmentPower(atom_expr, factor)

    def dictmarker(self, *tests):
        ret = []
        for i in range(0, len(tests), 2):
            ret.append((tests[i], tests[i + 1]))
        return ret

    def atom_dict(self, marker=NOTHING):
        if marker is NOTHING:
            return {}

        if isinstance(marker[0], tuple) and len(marker[0]) == 2:
            return TagSegmentDict(*marker)
        return TagSegmentSet(*marker)

    def atom_string(self, *strings):
        return ''.join(strings)

    def _one_or_more(self, one, *more, sign=None, segment=None):
        if not more:
            return one
        if sign is None:
            return segment(one, *more)
        return segment(sign, one, *more)

    _passby = TagTransformerStandard._passby
    _passby_segment = TagTransformerStandard._passby_segment
    _passby_single_segment = TagTransformerStandard._passby_single_segment
    or_test = partialmethod(_one_or_more, segment=TagSegmentOr)
    and_test = partialmethod(_one_or_more, segment=TagSegmentAnd)
    expr = partialmethod(_one_or_more, sign='|', segment=TagSegmentExpr)
    xor_expr = partialmethod(_one_or_more, sign='^', segment=TagSegmentExpr)
    and_expr = partialmethod(_one_or_more, sign='&', segment=TagSegmentExpr)
    funccall = partialmethod(_passby_segment, segment=TagSegmentFuncCall)
    get_item = partialmethod(_passby_segment, segment=TagSegmentGetItem)
    get_attr = partialmethod(_passby_segment, segment=TagSegmentGetAttr)
    arguments = partialmethod(_passby_segment, segment=TagSegmentArguments)
    atom_tuple = partialmethod(_passby_single_segment, segment=TagSegmentTuple)
    atom_list = partialmethod(_passby_single_segment, segment=TagSegmentList)
    output = partialmethod(_passby_segment, segment=TagSegmentOutput)
    subscript = partialmethod(_passby_segment, segment=TagSegmentSlice)
    not_ = partialmethod(_passby_segment, segment=TagSegmentNot)
    shift_expr = arith_expr = term
    testlist_comp = _passby
