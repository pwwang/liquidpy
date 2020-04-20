"""Parse the expression node {{ ... }}
Expression nodes could be complicated, we put this in a separate model
"""
from contextlib import suppress
import attr
from .defaults import LIQUID_LIQUID_FILTERS, LIQUID_RENDERED_APPEND
from .filters import LIQUID_FILTERS
from .stream import LiquidStream, safe_split
from .exceptions import (LiquidCodeTagExists,
                         LiquidSyntaxError,
                         LiquidExpressionFilterModifierException)
from .nodes import NodeVoid

class LiquidExpressionFilter:
    """One of the elements in {{x | y | z | ...}}
    So it could be a base value (x) or a filter (y, z, ...)"""

    @staticmethod
    def get_modifiers(filt):
        """Get the modifiers from a filter"""
        modifiers = {'?': False, '*': False, '@': False, '!': False,
                     '=': False, '?!': False, '?=': False, '$': False}
        filt_nomodifiers = filt.lstrip('?*@!$= \t')
        leading = filt[:(len(filt)-len(filt_nomodifiers))]
        # ?!, ?= go first
        for modifier in sorted(modifiers.keys(), key=len, reverse=True):
            mindex = leading.find(modifier)
            if mindex == -1:
                continue
            modifiers[modifier] = True
            leading = leading[:mindex] + leading[mindex + len(modifier):]

        # check if modifiers are compatible
        if ((modifiers['?'] or modifiers['!'] or modifiers['=']) and
                (modifiers['?!'] or modifiers['?='])):
            raise LiquidExpressionFilterModifierException(
                'Single ternary modifier (?/!/=) cannot be used'
                'together with ?! or ?='
            )
        if modifiers['?!'] and modifiers['?=']:
            raise LiquidExpressionFilterModifierException(
                'Positive/negative ternary modifier '
                '(?=/?!) cannot be used together'
            )
        if modifiers['?'] and (modifiers['='] or modifiers['!']):
            raise LiquidExpressionFilterModifierException(
                'Modifier (?) and (=/!) should not be '
                'used separately in one filter. Do you mean (?!/?=)?'
            )
        if modifiers['='] and modifiers['!']:
            raise LiquidExpressionFilterModifierException(
                'Modifier (=) and (!) cannot be used together'
            )

        leading = leading.replace(' ', '').replace('\t', '')
        if leading:
            raise LiquidExpressionFilterModifierException(
                f'Redundant modifiers found: {leading!r}'
            )

        return modifiers, filt_nomodifiers

    @staticmethod
    def parse_base_single(expr):
        """
        Parse the first part of an expression or
        when filter.isget is True, which makes available of this:
        {{x | a-b.c}} -> x['a-b'].c
        """
        try:
            # in case we have a float number
            # 1.2 or 1.3e-10
            float(expr)
            return expr
        except ValueError:
            pass

        dots = safe_split(expr, '.')
        ret = dots.pop(0)

        for dot in dots:
            dstream = LiquidStream.from_string(dot)
            dot, dim = dstream.until(['[', '('])
            if dim:
                dim = dim + dstream.dump()

            # dodots(a, 'b')[1]
            dim = dim or ''
            ret = (f"{NodeLiquidExpression.LIQUID_DOT_FUNC_NAME}"
                   f"({ret}, {dot!r}){dim}")
        return ret

    @staticmethod
    def parse_base(expr):
        """Parse the first part of  {{ x | y | z}}"""
        # what about "(1,2), (3,4)",
        #            "((1,2), (3,4))",
        #            "(((1,2), (3,4)))",
        #            "(((1,2)))"
        # (((1))) and "((1,2), [3,4])"? ((((1,2), 3), (4,5)))
        # 1. remove redundant (): ->
        #   "(1,2), (3,4)", "(1,2), (3,4)", "(1,2), (3,4)", (1,2)
        #   (1) and "((1,2), [3,4])"? ((1,2), 3), (4,5)
        lenexpr = len(expr)
        lbracket = lenexpr - len(expr.lstrip('('))
        rbracket = lenexpr - len(expr.rstrip(')'))
        minbrkt = min(lbracket, rbracket)
        if minbrkt > 0:
            expr = '(' + expr[minbrkt:-minbrkt] + ')'

        parts = LiquidStream.from_string(expr).split(',')
        # if we can split, ok, we have removed all redundant ()
        if len(parts) > 1:
            return '({})'.format(
                ', '.join(LiquidExpressionFilter.parse_base_single(part)
                          for part in parts)
            )
        if minbrkt > 0:
            # if we cannot, like (1), (1,2), ((1,2), [3,4]),
            # try to remove the bracket again ->
            #   "1", "1,2", "(1,2), [3,4]"
            parts = LiquidStream.from_string(expr[1:-1]).split(',')
            if len(parts) > 1:
                return '({})'.format(', '.join(
                    LiquidExpressionFilter.parse_base_single(part)
                    for part in parts
                ))
        return LiquidExpressionFilter.parse_base_single(parts[0])

    def __init__(self, expr):
        if not expr:
            raise LiquidExpressionFilterModifierException('No filter specified')
        self.modifiers, expr = LiquidExpressionFilter.get_modifiers(expr)
        self.func, self.args, self.isget = self._normalize_expr(expr)

    def _normalize_expr(self, expr):
        if not expr and self.modifiers['?']:
            return '_', None, False

        expr_parts = LiquidStream.from_string(expr).split(':', limit=1)
        # shortcut for lambda
        if len(expr_parts) == 1:
            expr_parts.append(None)

        isget = False
        if not expr_parts[0] or expr_parts[0].startswith('lambda'):
            if self.modifiers['@']:
                raise LiquidExpressionFilterModifierException(
                    'Liquid modifier should not go with lambda shortcut.'
                )
            expr_parts[0] = expr_parts[0] or 'lambda _'
            expr_parts[0] = '(%s: (%s))' % (expr_parts[0], expr_parts[1])
            expr_parts[1] = None

        elif expr_parts[0][0] in ('.', '['):
            if self.modifiers['*'] or self.modifiers['@']:
                raise LiquidExpressionFilterModifierException(
                    'Attribute filter should not have modifiers'
                )
            isget = True

        elif self.modifiers['@']:
            if expr_parts[0] not in LIQUID_FILTERS:
                raise LiquidExpressionFilterModifierException(
                    f"Unknown liquid filter: '@{expr_parts[0]}'"
                )
            expr_parts[0] = f'{LIQUID_LIQUID_FILTERS}[{expr_parts[0]!r}]'

        args = (None if expr_parts[1] is None
                else LiquidStream.from_string(expr_parts[1]).split(','))

        # {{x | _}} => x
        if args is None and not isget and expr_parts[0] != '_':
            # {{x | y}} -> y(x)
            args = ['_']

        elif (args is not None and not isget and
              not any(arg[:1] == '_' and (not arg[1:] or arg[1:].isdigit())
                      for arg in args)):
            args.insert(0, '_')

        return expr_parts[0], args, isget

    def parse(self, base):
        """Parse the filter according to the base value"""
        if self.isget:
            base = LiquidExpressionFilter.parse_base_single(base + self.func)
            if self.args is None:
                return base
            return '%s(%s)' % (base, ', '.join(self.args))

        if self.func == '_' and self.args is None:
            # allow _ to return the base
            # {{x | ? | !_ | = :_+1}}
            # .render(x = 0) => 0
            # .render(x = 1) => 2
            return base

        argprefix = ('*' if base[0] + base[-1] == '()' and self.modifiers['*']
                     else '')
        for i, arg in enumerate(self.args):
            if arg == '_':
                self.args[i] = argprefix + base
            elif arg[:1] == '_' and arg[1:].isdigit():
                self.args[i] = '%s[%d]' % (base, int(arg[1:]) - 1)
        return '{}({})'.format(self.func, ', '.join(self.args))


@attr.s(kw_only=True)
class NodeLiquidExpression(NodeVoid):
    """Node like {{ ... }}}"""

    name = attr.ib(default='<liquid_expr>')
    # code is not necessary as we need this to parse mixed expressions
    code = attr.ib(default=None)

    LIQUID_DOT_FUNC_NAME = '_liquid_dodots_function'

    def _parse_ternary(self, exprs, base):
        # pylint: disable=too-many-branches
        conditions, truthy, falsy = [], [], []
        first_expr = exprs.pop(0)
        if first_expr.modifiers['?']:
            first_expr.modifiers['?'] = False
            conditions.append(first_expr)
            container = conditions
        elif first_expr.modifiers['?!']:
            first_expr.modifiers['?!'] = False
            falsy.append(first_expr)
            container = falsy
        else: # ?=
            first_expr.modifiers['?='] = False
            truthy.append(first_expr)
            container = truthy
        # make sure
        # {{x | ? | !_ | =:_+1 | ? | !_ | =:_+1}}
        # grouped to:
        # {{x | conditions | falsy | truthy ...}}
        sub_ternary = sub_summary_counter = 0
        summary = None
        for i, filt in enumerate(exprs):
            if filt.modifiers['$']:
                sub_summary_counter += 1
                if sub_summary_counter > sub_ternary:
                    summary = exprs[i:]
                    break

            if (filt.modifiers['?'] or
                    filt.modifiers['?!'] or
                    filt.modifiers['?=']):
                sub_ternary += 1

            if sub_ternary:
                container.append(filt)
                continue

            if filt.modifiers['!']:
                if falsy:
                    raise LiquidSyntaxError(
                        "False action has already been defined",
                        self.context
                    )
                container = falsy
            elif filt.modifiers['=']:
                if truthy:
                    raise LiquidSyntaxError(
                        "True action has already been defined",
                        self.context
                    )
                container = truthy
            container.append(filt)

        if not truthy and not falsy:
            raise LiquidSyntaxError(
                "Missing True/False actions for ternary filter",
                self.context
            )

        ret = '((%s) if (%s) else (%s))' % (
            self._parse_exprs(truthy, base) if truthy else base,
            self._parse_exprs(conditions, base) if conditions else base,
            self._parse_exprs(falsy, base) if falsy else base,
        )
        if not summary:
            return ret

        return self._parse_exprs(summary, ret)

    def _parse_exprs(self, exprs, base):
        if (exprs[0].modifiers['?'] or exprs[0].modifiers['?!'] or
                exprs[0].modifiers['?=']):
            return self._parse_ternary(exprs, base)

        for i, filt in enumerate(exprs):
            if (filt.modifiers['?'] or filt.modifiers['?!'] or
                    filt.modifiers['?=']):
                return self._parse_exprs(exprs[i:], base)
            base = filt.parse(base)

        return base

    def _parse(self):
        """Start to parse the node"""
        #if not string: # Empty node
        #	self.parser.raise_ex('Nothing found for expression')
        with suppress(LiquidCodeTagExists), self.shared_code.tag(
                NodeLiquidExpression.LIQUID_DOT_FUNC_NAME
        ) as tagged:
            tagged.add_line('')
            tagged.add_line(
                f'def {NodeLiquidExpression.LIQUID_DOT_FUNC_NAME}(obj, dot):'
            )
            tagged.indent()
            tagged.add_line("'''Allow dot operation for a.b and a['b']'''")
            tagged.add_line('try:')
            tagged.indent()
            tagged.add_line('return getattr(obj, dot)')
            tagged.dedent()
            tagged.add_line('except (AttributeError, TypeError):')
            tagged.indent()
            tagged.add_line('return obj[dot]')
            tagged.dedent()
            tagged.dedent()
            tagged.add_line('')

        exprs = safe_split(self.attrs, '|')
        base = LiquidExpressionFilter.parse_base(exprs.pop(0))

        if not exprs:
            return base

        try:
            exprs = [LiquidExpressionFilter(expr) for expr in exprs]
        except LiquidExpressionFilterModifierException as fmex:
            raise LiquidSyntaxError(str(fmex), self.context) from None
        return self._parse_exprs(exprs, base)

    def parse_node(self):
        """@API
        Start parsing the node
        """
        super().parse_node()
        parsed = self._parse()
        self.code.add_line(f"{LIQUID_RENDERED_APPEND}({parsed})",
                           self.context)
