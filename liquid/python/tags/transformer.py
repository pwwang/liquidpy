"""The segments and transformer for liquidpy in python mode"""
# pylint: disable=relative-beyond-top-level
from functools import partialmethod
from lark import v_args, Token
from ...config import LIQUID_FILTERS_ENVNAME
from ...tags.transformer import (
    render_segment,
    TagSegment,
    TagSegmentComparison,
    TagSegmentVar as TagSegmentVarStandard,
    TagTransformer as TagTransformerStandard
)
from ...utils import NOTHING
from ...filters import EmptyDrop

class TagSegmentVar(TagSegmentVarStandard):
    """Varaible segment in python mode. There will be no EmptyDrop object
    as rendered"""
    def render(self, local_vars, global_vars):
        """Get the value of a variable from envs"""
        var = super().render(local_vars, global_vars)
        if isinstance(var, EmptyDrop):
            varname = str(self.data[0])
            return local_vars.get(varname, global_vars.get(varname))
        return var

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
        # type: (dict, dict) -> Any
        """render the segment"""
        for data in self.data:
            data = render_segment(data, local_vars, global_vars)
            if data:
                return data
        return False

class TagSegmentAnd(TagSegment):
    """And statement in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
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
        # type: (dict, dict) -> Any
        """render the segment"""
        return not render_segment(self.data[0], local_vars, global_vars)

class TagSegmentGetAttr(TagSegment):
    """Getattr operation in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        obj = render_segment(self.data[0], local_vars, global_vars)
        try:
            return getattr(obj, self.data[1])
        except AttributeError as exc:
            try:
                return obj[self.data[1]]
            except (KeyError, TypeError):
                raise AttributeError(
                    f'{type(obj).__name__!r} object has '
                    f'no attribute {self.data[1]!r}'
                ).with_traceback(exc.__traceback__) from None

class TagSegmentGetItem(TagSegment):
    """Getitem operation in python"""

    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        return render_segment(self.data[0], local_vars, global_vars)[
            render_segment(self.data[1], local_vars, global_vars)
        ]

class TagSegmentExpr(TagSegment):
    """Expressions in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        sign = str(self.data[0])
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
        # type: (dict, dict) -> Any
        """render the segment"""
        data1 = render_segment(self.data[0], local_vars, global_vars)
        data2 = render_segment(self.data[1], local_vars, global_vars)
        return data1 ** data2

class TagSegmentFactor(TagSegment):
    """Factor expression in python"""

    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
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
        # type: (dict, dict) -> Any
        """render the segment"""
        func = render_segment(self.data[0], local_vars, global_vars)
        if self.data[1] is None:
            return func()
        args, kwargs = render_segment(self.data[1], local_vars, global_vars)
        return func(*args, **kwargs)

class TagSegmentTuple(TagSegment):
    """Tuple literals in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        if not self.data or self.data[0] is NOTHING:
            return ()
        return tuple(render_segment(data, local_vars, global_vars)
                     for data in self.data[0])

class TagSegmentList(TagSegment):
    """List literals in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        if not self.data or self.data[0] is NOTHING:
            return []
        return list(render_segment(data, local_vars, global_vars)
                    for data in self.data[0])

class TagSegmentSet(TagSegment):
    """Set literals in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        return set(render_segment(data, local_vars, global_vars)
                   for data in self.data)

class TagSegmentDict(TagSegment):
    """Dict literals in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        return {
            render_segment(key, local_vars, global_vars):
            render_segment(val, local_vars, global_vars)
            for key, val in self.data
        }

class TagSegmentSlice(TagSegment):
    """Slice objects in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        if len(self.data) == 1:
            return render_segment(self.data[0], local_vars, global_vars)
        return slice(*(render_segment(data, local_vars, global_vars)
                       for data in self.data))

class TagSegmentLambda(TagSegment):
    """Lambda objects in python"""
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        arglist, body = self.data
        al_args, al_kwargs = arglist.render(
            local_vars, global_vars, as_is=True
        ) if arglist else ([], {})
        al_kwargs_keys = list(al_kwargs.keys())
        len_al_args = len(al_args)

        def lambdafunc(*args, **kwargs):
            local_vars_inside = local_vars.copy()
            local_vars_inside.update(al_kwargs)
            local_vars_inside.update(kwargs)
            for i, arg in enumerate(args):
                if i < len_al_args:
                    local_vars_inside[al_args[i]] = arg
                else:
                    key = al_kwargs_keys[i - len_al_args]
                    if key in kwargs:
                        raise TypeError(f'Argument {key!r} got multiple values')
                    local_vars_inside[key] = arg

            return render_segment(body, local_vars_inside, global_vars)

        return lambdafunc

class TagSegmentFilter(TagSegment):
    """Filter segment"""
    # pylint: disable=no-self-use
    def _no_such_filter(self, name_token, exc_wrapper=KeyError):
        error = exc_wrapper(f"No such filter: {str(name_token)!r}")
        try:
            error.lineno = name_token.line
            error.colno = name_token.column
        except AttributeError:
            pass
        return error

    def _get_filter_by_name(self, local_vars, global_vars,
                            name_token, complex=False):
        # pylint: disable=redefined-builtin
        if not complex:
            filtname = str(name_token)
            filter_func = global_vars[LIQUID_FILTERS_ENVNAME].get(
                filtname, local_vars.get(
                    filtname, global_vars.get(filtname, NOTHING)
                )
            )
            if filter_func is NOTHING:
                raise self._no_such_filter(name_token)
            return filter_func
        try:
            filter_func = render_segment(name_token, local_vars, global_vars)
        except Exception as exc:
            raise self._no_such_filter(name_token, type(exc)) from None
        return filter_func

    def _render_lambda(self, local_vars, global_vars):
        return self.data[0].render(local_vars, global_vars)

    def _render_ternary(self, local_vars, global_vars):
        # ternary
        condfilter, truth, falsity = self.data

        def filter_ternary(base):
            cond = (condfilter.render(local_vars, global_vars)(base)
                    if condfilter
                    else base)
            if cond:
                return (truth.render(local_vars, global_vars)(base)
                        if isinstance(truth, TagSegmentFilter)
                        else base
                        if truth is None
                        else render_segment(truth, local_vars, global_vars))
            return (falsity.render(local_vars, global_vars)(base)
                    if isinstance(falsity, TagSegmentFilter)
                    else base
                    if falsity is None
                    else render_segment(falsity, local_vars, global_vars))

        return filter_ternary

    def _render_normal(self,  # pylint: disable=too-many-arguments
                       local_vars,
                       global_vars,
                       filter_name,
                       filter_arg,
                       filter_type):
        if filter_arg is None:
            filter_args, filter_kwargs = [], {}
        else:
            local_vars_copy = local_vars.copy()
            local_vars_copy['_'] = NOTHING
            filter_args, filter_kwargs = filter_arg.render(
                local_vars_copy, global_vars
            )

        filter_func = self._get_filter_by_name(
            local_vars, global_vars, filter_name, filter_type == 'complex'
        )

        def filter_function(base):
            args = filter_args
            if NOTHING in args:
                args[args.index(NOTHING)] = base
            else:
                args.insert(0, base)

            return filter_func(*args, **filter_kwargs)
        return filter_function

    def _render_other(self,  # pylint: disable=too-many-arguments
                      local_vars,
                      global_vars,
                      filter_name,
                      filter_arg,
                      filter_type):
        if filter_arg is None:
            filter_args, filter_kwargs = [], {}
        else:
            filter_args, filter_kwargs = filter_arg.render(
                local_vars, global_vars
            )
        filtname = str(filter_name)

        def filter_function(base):
            if filter_type == 'dot':
                try:
                    filter_func = getattr(base, filtname)
                except AttributeError:
                    raise self._no_such_filter(
                        filter_name, AttributeError
                    ) from None
                return filter_func(*filter_args, **filter_kwargs)

            if filter_type == 'subscript':
                try:
                    filter_func = base[filtname]
                except (KeyError, TypeError) as exc:
                    raise self._no_such_filter(
                        filter_name, type(exc)
                    ) from None

                return filter_func(*filter_args, **filter_kwargs)
            # start, keyword
            subtype = 'normal'
            subname = filter_name
            if isinstance(filter_name, tuple):
                subname, subtype = filter_name
            filter_func = self._get_filter_by_name(
                local_vars, global_vars, subname, subtype == 'complex'
            )
            if filter_type == 'star':
                return filter_func(*base, *filter_args, **filter_kwargs)
            return filter_func(*filter_args, **base, **filter_kwargs)

        return filter_function

    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        """render the segment"""
        if len(self) == 1: # lambda
            return self._render_lambda(local_vars, global_vars)

        if len(self) == 2: # varname: arguments
            filter_name, filter_arg = self.data
            filter_type = 'normal'
            if isinstance(filter_name, tuple):
                filter_name, filter_type = filter_name

            if filter_type in ('normal', 'complex'):
                return self._render_normal(local_vars, global_vars,
                                           filter_name, filter_arg, filter_type)

            return self._render_other(local_vars, global_vars,
                                      filter_name, filter_arg,
                                      filter_type)

        return self._render_ternary(local_vars, global_vars)

@v_args(inline=True)
class TagTransformer(TagTransformerStandard):
    """Transformer for python grammar"""
    # pylint: disable=no-self-use

    def test(self, value, cond=NOTHING, false_value=NOTHING):
        """The rule test: or_test ("if" or_test "else" test)? | lambdef"""
        if cond is NOTHING and false_value is NOTHING:
            return value
        return TagSegmentIfelse(value, cond, false_value)

    # pylint: disable=signature-differs, arguments-differ
    def comparison(self, expr, *op_and_exprs):
        """The rule comparison: expr (_comp_op expr)*"""
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
        """The rule term: factor (_mul_op factor)*"""
        if not more:
            return one
        return TagSegmentExpr(
            more[0], one, *(mor for i, mor in enumerate(more) if i % 2)
        )

    def factor(self, factor_op_or_power, factor=NOTHING):
        """The rule factor: _factor_op factor | power"""
        if factor is NOTHING:
            return factor_op_or_power

        return TagSegmentFactor(factor_op_or_power, factor)

    def power(self, atom_expr, factor=NOTHING):
        """The rule power: atom_expr ("**" factor)?"""
        if factor is NOTHING:
            return atom_expr
        return TagSegmentPower(atom_expr, factor)

    def dictmarker(self, *tests):
        """The dictmarker rule:
        dictmarker: test ":" test ("," test ":" test)* [","]
        """
        ret = []
        for i in range(0, len(tests), 2):
            ret.append((tests[i], tests[i + 1]))
        return ret

    def atom_dict(self, marker=NOTHING):
        """The rule atom_dict: "{" (dictmarker|testlist_comp)? "}" """
        if marker is NOTHING:
            return {}

        if isinstance(marker[0], tuple) and len(marker[0]) == 2:
            return TagSegmentDict(*marker)
        return TagSegmentSet(*marker)

    def atom_string(self, *strings):
        """The rule atom_string: string+ """
        return ''.join(strings)

    def _filter_type(self, var, ftype):
        return (var, ftype)

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
    atom_tuple = partialmethod(_passby_single_segment, segment=TagSegmentTuple)
    atom_list = partialmethod(_passby_single_segment, segment=TagSegmentList)
    subscript = partialmethod(_passby_segment, segment=TagSegmentSlice)
    not_ = partialmethod(_passby_segment, segment=TagSegmentNot)
    test_filter = partialmethod(_passby_segment, segment=TagSegmentFilter)
    lambdef = partialmethod(_passby_segment, segment=TagSegmentLambda)
    var = partialmethod(_passby_segment, segment=TagSegmentVar)
    shift_expr = arith_expr = term
    testlist_comp = _passby
    dot_filter = partialmethod(_filter_type, ftype='dot')
    star_filter = partialmethod(_filter_type, ftype='star')
    keyword_filter = partialmethod(_filter_type, ftype='keyword')
    subscript_filter = partialmethod(_filter_type, ftype='subscript')
    complex_filter = partialmethod(_filter_type, ftype='complex')
