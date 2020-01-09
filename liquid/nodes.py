"""
The nodes supported by liquidpy
"""
#pylint:disable=too-many-statements,protected-access,attribute-defined-outside-init
import logging
from .stream import LiquidStream
from .filters import LIQUID_FILTERS
from .defaults import (
    LIQUID_LOGGER_NAME,
    LIQUID_MODES,
    LIQUID_LIQUID_FILTERS,
    LIQUID_COMPILED_RR_APPEND,
    LIQUID_COMPILED_RR_EXTEND,
    LIQUID_COMPILED_RENDERED,
)

def push_history(func):
    """Push the node to the history"""
    def retfunc(self, *args, **kwargs):
        """Push the tag in history and then do the stuff"""
        func(self, *args, **kwargs)
        self.parser.history.append(self.name)
    return retfunc

def push_both(func):
    """Push the node to both stack and history"""
    def retfunc(self, *args, **kwargs):
        """Push the tag in both stack and history and then do the stuff"""
        self.parser.stack.append(self.name)
        func(self, *args, **kwargs)
        self.parser.history.append(self.name)
    return retfunc

def pop_stack(func):
    """Pop the node from the stack"""
    def retfunc(self, *args, **kwargs):
        """Pop the tag in stack and then do the stuff"""
        last = self.parser.stack.pop() if self.parser.stack else None
        if last != self.name:
            if last:
                self.parser.raise_ex(
                    "Unmatched end tag: 'end{}', expect 'end{}'".format(
                        self.name,
                        last
                    )
                )
            self.parser.raise_ex(
                "Unmatched end tag: 'end{}'".format(self.name)
            )
        func(self, *args, **kwargs)
    return retfunc

def dedent(func):
    """Dedent the code"""
    def retfunc(self, *args, **kwargs):
        """Do the stuff and dedent the code"""
        func(self, *args, **kwargs)
        self.parser.code.dedent()
    return retfunc

class _FilterModifierException(Exception):
    """When incompatible modifiers are assigned to a filter"""

class _Filter:
    """One of the elements in {{x | y | z | ...}}
    So it could be a base value (x) or a filter (y, z, ...)"""

    @staticmethod
    def get_modifiers(filt):
        """Get the modifiers from a filter"""
        modifiers = {'?': False,
                     '*': False,
                     '@': False,
                     '!': False,
                     '=': False,
                     '?!': False,
                     '?=': False,
                     '$': False}
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
        if ((modifiers['?'] or
             modifiers['!'] or
             modifiers['=']) and
                (modifiers['?!'] or
                 modifiers['?='])):
            raise _FilterModifierException(
                'Single ternary modifier (?/!/=) cannot be used' \
                'together with ?! or ?='
            )
        if modifiers['?!'] and modifiers['?=']:
            raise _FilterModifierException(
                'Positive/negative ternary modifier ' \
                '(?=/?!) cannot be used together'
            )
        if modifiers['?'] and (modifiers['='] or modifiers['!']):
            raise _FilterModifierException(
                'Modifier (?) and (=/!) should not be ' \
                'used separately in one filter. Do you mean (?!/?=)?'
            )
        if modifiers['='] and modifiers['!']:
            raise _FilterModifierException(
                'Modifier (=) and (!) cannot be used together'
            )

        leading = leading.replace(' ', '').replace('\t', '')
        if leading:
            raise _FilterModifierException(
                'Redundant modifiers found: {!r}'.format(leading)
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

        dots = LiquidStream.from_string(expr).split('.')
        ret = dots.pop(0)

        for dot in dots:
            dstream = LiquidStream.from_string(dot)
            dot, dim = dstream.until(['[', '('])
            if dim:
                dim = dim + dstream.dump()

            # dodots(a, 'b')[1]
            ret = '{}({}, {!r}){}'.format(
                NodeExpression.LIQUID_DOT_FUNC_NAME,
                ret,
                dot,
                dim or ''
            )
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
                ', '.join(_Filter.parse_base_single(part)
                          for part in parts)
            )
        if minbrkt > 0:
            # if we cannot, like (1), (1,2), ((1,2), [3,4]),
            # try to remove the bracket again ->
            #   "1", "1,2", "(1,2), [3,4]"
            parts = LiquidStream.from_string(expr[1:-1]).split(',')
            if len(parts) > 1:
                return '({})'.format(
                    ', '.join(_Filter.parse_base_single(part)
                              for part in parts)
                )
        return _Filter.parse_base_single(parts[0])

    def __init__(self, expr):
        if not expr:
            raise _FilterModifierException('No filter specified')
        self.modifiers, expr = _Filter.get_modifiers(expr)
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
                raise _FilterModifierException(
                    'Liquid modifier should not go with lambda shortcut.'
                )
            expr_parts[0] = expr_parts[0] or 'lambda _'
            expr_parts[0] = '(%s: (%s))' % (expr_parts[0], expr_parts[1])
            expr_parts[1] = None

        elif expr_parts[0][0] in ('.', '['):
            if self.modifiers['*'] or self.modifiers['@']:
                raise _FilterModifierException(
                    'Attribute filter should not have modifiers'
                )
            isget = True

        elif self.modifiers['@']:
            if expr_parts[0] not in LIQUID_FILTERS:
                raise _FilterModifierException(
                    "Unknown liquid filter: '@{}'".format(expr_parts[0])
                )
            expr_parts[0] = '{}[{!r}]'.format(LIQUID_LIQUID_FILTERS,
                                              expr_parts[0])

        args = None \
            if expr_parts[1] is None \
            else LiquidStream.from_string(expr_parts[1]).split(',')

        # {{x | _}} => x
        if args is None and not isget and expr_parts[0] != '_':
            # {{x | y}} -> y(x)
            args = ['_']

        elif (args is not None and
              not isget and
              not any(arg[:1] == '_' and (not arg[1:] or
                                          arg[1:].isdigit())
                      for arg in args)):
            args.insert(0, '_')

        return expr_parts[0], args, isget

    def parse(self, base):
        """Parse the filter according to the base value"""
        if self.isget:
            base = _Filter.parse_base_single(base + self.func)
            if self.args is None:
                return base
            return '%s(%s)' % (base, ', '.join(self.args))

        if self.func == '_' and self.args is None:
            # allow _ to return the base
            # {{x | ? | !_ | = :_+1}}
            # .render(x = 0) => 0
            # .render(x = 1) => 2
            return base

        argprefix = '*' \
                    if base[0] + base[-1] == '()' and self.modifiers['*'] \
                    else ''
        for i, arg in enumerate(self.args):
            if arg == '_':
                self.args[i] = argprefix + base
            elif arg[:1] == '_' and arg[1:].isdigit():
                self.args[i] = '%s[%d]' % (base, int(arg[1:]) - 1)
        return '{}({})'.format(self.func, ', '.join(self.args))

class _Node:
    """The base class"""

    def __init__(self, parser):
        """Initialize the node"""
        self.parser = parser
        self.name = self.__class__.__name__[4:].lower()

    def start(self, string):
        """Start to compile the node"""

    @pop_stack
    @dedent
    def end(self):
        """end node hit"""

class NodeMode(_Node):
    """
    Node '{% mode ... %}'
    """

    def _set_mode(self, mode):
        """Set the mode"""
        if mode not in LIQUID_MODES:
            self.parser.raise_ex('Not a valid mode: {!r}'.format(mode))
        self.parser.mode = mode

    def _set_loglevel(self, loglevel):
        """Set the loglevel"""
        loglevel = loglevel.upper()
        if not NodeMode._is_loglevel(loglevel):
            self.parser.raise_ex(
                'Not a valid loglevel: {!r}'.format(loglevel)
            )
        logging.getLogger(LIQUID_LOGGER_NAME).setLevel(loglevel)

    @staticmethod
    def _is_loglevel(loglevel):
        """Tell if a string is a valid loglevel"""
        return isinstance(logging.getLevelName(loglevel), int)

    @push_history
    def start(self, string):
        """Start to compile the node"""
        if not string:
            self.parser.raise_ex('Expecting a mode value')
        parts = string.split()
        if len(parts) == 1:
            parts = parts[0].split(',')
        parts = [part.strip() for part in parts]
        if len(parts) > 2:
            self.parser.raise_ex('Mode can only take at most 2 values')

        if len(parts) == 1:
            if NodeMode._is_loglevel(parts[0].upper()):
                self._set_loglevel(parts[0])
            else:
                self._set_mode(parts[0])

        else:
            part1, part2 = parts[:2]
            if NodeMode._is_loglevel(part1.upper()):
                self._set_loglevel(part1)
                self._set_mode(part2)
            else:
                self._set_mode(part1)
                self._set_loglevel(part2)

class NodeIf(_Node):
    """
    Node '{% if ... %} {% endif %}'
    """
    @push_both
    def start(self, string, prefix='if ', suffix=''): # pylint:disable=arguments-differ
        """Start to compile the node"""
        if not string:
            self.parser.raise_ex(
                'No expressions for statement "{}"'.format(self.name)
            )
        sstream = LiquidStream.from_string(string)
        # merge multiple lines
        #sstream = LiquidStream.from_string(' '.join(sstream.split(['\\\n'])))
        prestr, bracket = sstream.until(['`'])
        ifexpr = prefix
        if not bracket:
            ifexpr += prestr
        while bracket:
            expr, endbrkt = sstream.until(['`'])

            if endbrkt:
                ifexpr += prestr + NodeExpression(self.parser)._parse(expr)
                prestr, bracket = sstream.until(['`'])
                if not bracket:
                    ifexpr += prestr
            else: # pragma: no cover
                # this technically will not  happen
                # because if there is only on `, there should be a syntax error
                ifexpr += prestr + '`' + expr + endbrkt
                bracket = ''
        ifexpr = (ifexpr[:-1] if ifexpr[-1] == ':' else ifexpr) + suffix
        self.parser.code.add_line(ifexpr + ':', self.parser)
        self.parser.code.indent()

class NodeElse(_Node):
    """
    Node '{% else/else if... %}'
    """

    @push_history
    def start(self, string):
        """Start to compile the node"""
        if (not self.parser.stack or
                self.parser.stack[-1] not in ('case', 'if', 'unless')):
            self.parser.raise_ex(
                '"else" must be in an if/unless/case statement'
            )
        # see if it is else if
        parts = string.split(maxsplit=1)
        if not parts:
            self.parser.code.dedent()
            self.parser.code.add_line('else:')
            self.parser.code.indent()
        elif parts[0] == 'if' and self.parser.stack[-1] == 'if':
            ifnode = NodeIf(self.parser)
            self.parser.code.dedent()
            ifnode.start(parts[1] if len(parts) > 1 else '', 'elif ')
            ifnode.end()
            self.parser.code.indent()
        else:
            self.parser.raise_ex(
                '"else" should not be followed by any expressions'
            )

class NodeElseif(_Node):
    """
    Node '{% elseif ... %} '
    """

    @push_history
    def start(self, string):
        """Start to compile the node"""
        if not self.parser.stack or self.parser.stack[-1] != 'if':
            self.parser.raise_ex(
                '"elseif/elif/elsif" must be in an "if/unless" statement'
            )
        ifnode = NodeIf(self.parser)
        self.parser.code.dedent()
        ifnode.start(string, 'elif ')
        ifnode.end()
        self.parser.code.indent()

NodeElif = NodeElsif = NodeElseif

class NodeLiteral(_Node):
    """
    Literal node
    """
    def start(self, string):
        """Start to compile the node"""
        if not string:
            return
        lines = string.splitlines(keepends=True)
        if len(lines) > 1:
            self.parser.code.add_line('{}(['.format(LIQUID_COMPILED_RR_EXTEND))
            self.parser.code.indent()
            for line in lines:
                self.parser.code.add_line('{!r},'.format(line), self.parser)
            self.parser.code.dedent()
            self.parser.code.add_line('])')
        else:
            self.parser.code.add_line('{}({!r})'.format(
                LIQUID_COMPILED_RR_APPEND, lines[0]), self.parser)

NodeRaw = NodeLiteral

class NodeExpression(_Node):
    """
    Expression node
    """
    LIQUID_DOT_FUNC_NAME = '_liquid_dodots_function'

    def _parse_ternary(self, exprs, base):

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
                    self.parser.raise_ex(
                        'False action has already been defined'
                    )
                container = falsy
            elif filt.modifiers['=']:
                if truthy:
                    self.parser.raise_ex(
                        'True action has already been defined'
                    )
                container = truthy
            container.append(filt)

        if not truthy and not falsy:
            self.parser.raise_ex(
                'Missing True/False actions for ternary filter'
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
        if (exprs[0].modifiers['?'] or
                exprs[0].modifiers['?!'] or
                exprs[0].modifiers['?=']):
            return self._parse_ternary(exprs, base)

        for i, filt in enumerate(exprs):
            if (filt.modifiers['?'] or
                    filt.modifiers['?!'] or
                    filt.modifiers['?=']):
                return self._parse_exprs(exprs[i:], base)
            base = filt.parse(base)

        return base

    def _parse(self, string):
        """Start to parse the node"""
        #if not string: # Empty node
        #	self.parser.raise_ex('Nothing found for expression')

        if not getattr(self.parser.precode,
                       NodeExpression.LIQUID_DOT_FUNC_NAME,
                       None):
            setattr(self.parser.precode,
                    NodeExpression.LIQUID_DOT_FUNC_NAME,
                    True)
            self.parser.precode.add_line(
                'def {}(obj, dot):'.format(
                    NodeExpression.LIQUID_DOT_FUNC_NAME
                )
            )
            self.parser.precode.indent()
            self.parser.precode.add_line('try:')
            self.parser.precode.indent()
            self.parser.precode.add_line('return getattr(obj, dot)')
            self.parser.precode.dedent()
            self.parser.precode.add_line(
                'except (AttributeError, TypeError):'
            )
            self.parser.precode.indent()
            self.parser.precode.add_line('return obj[dot]')
            self.parser.precode.dedent()
            self.parser.precode.dedent()
            self.parser.precode.add_line('')

        sstream = LiquidStream.from_string(string)
        exprs = sstream.split('|')
        base = _Filter.parse_base(exprs.pop(0))

        if not exprs:
            return base

        try:
            exprs = [_Filter(expr) for expr in exprs]
        except _FilterModifierException as fmex:
            self.parser.raise_ex(str(fmex))
        return self._parse_exprs(exprs, base)

    @push_history
    def start(self, string):
        """Start to compile the node"""
        self.parser.code.add_line(
            '{}({})'.format(
                LIQUID_COMPILED_RR_APPEND,
                self._parse(string)
            ),
            self.parser
        )

class NodeFor(_Node):
    """
    Node '{% for ... %} {% endfor %}'
    """
    LIQUID_FORLOOP_CLASS = '_Liquid_forloop_class'

    @push_both
    def start(self, string):
        """Start to compile the node"""
        # i, v in x | range

        if not getattr(self.parser.precode,
                       NodeFor.LIQUID_FORLOOP_CLASS,
                       None):
            setattr(self.parser.precode, NodeFor.LIQUID_FORLOOP_CLASS, True)

            self.parser.precode.add_line(
                'class {}:'.format(NodeFor.LIQUID_FORLOOP_CLASS)
            )
            self.parser.precode.indent()
            self.parser.precode.add_line('def __init__(self, iterable):')
            self.parser.precode.indent()
            self.parser.precode.add_line(
                'self._iterable = [it for it in iterable]'
            )
            self.parser.precode.add_line('self.index0 = -1')
            self.parser.precode.add_line('self.length = len(self._iterable)')
            self.parser.precode.dedent()
            self.parser.precode.add_line('@property')
            self.parser.precode.add_line('def first(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self.index0 == 0')
            self.parser.precode.dedent()
            self.parser.precode.add_line('@property')
            self.parser.precode.add_line('def last(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self.index == self.length')
            self.parser.precode.dedent()
            self.parser.precode.add_line('@property')
            self.parser.precode.add_line('def index(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self.index0 + 1')
            self.parser.precode.dedent()
            self.parser.precode.add_line('@property')
            self.parser.precode.add_line('def rindex(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self.length - self.index0')
            self.parser.precode.dedent()
            self.parser.precode.add_line('@property')
            self.parser.precode.add_line('def rindex0(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self.rindex - 1')
            self.parser.precode.dedent()
            self.parser.precode.add_line('def __iter__(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('return self')
            self.parser.precode.dedent()
            self.parser.precode.add_line('def __next__(self):')
            self.parser.precode.indent()
            self.parser.precode.add_line('self.index0 += 1')
            self.parser.precode.add_line('if self.index > self.length:')
            self.parser.precode.indent()
            self.parser.precode.add_line('raise StopIteration')
            self.parser.precode.dedent()
            self.parser.precode.add_line('ret = [self]')
            self.parser.precode.add_line(
                'if isinstance(self._iterable[self.index0], (list, tuple)):'
            )
            self.parser.precode.indent()
            self.parser.precode.add_line(
                'ret.extend(self._iterable[self.index0])'
            )
            self.parser.precode.dedent()
            self.parser.precode.add_line('else:')
            self.parser.precode.indent()
            self.parser.precode.add_line(
                'ret.append(self._iterable[self.index0])'
            )
            self.parser.precode.dedent()
            self.parser.precode.add_line('return ret')
            self.parser.precode.dedent()
            self.parser.precode.dedent()

        from . import _check_envs
        if string and string[-1] == ':':
            string = string[:-1]
        parts = string.split(' in ', 1)
        if len(parts) == 1:
            self.parser.raise_ex(
                'Statement "for" expects format: "for var1, var2 in expr"'
            )
        _check_envs({lvar.strip():1 for lvar in parts[0].split(',')})

        # forloop for nesting fors
        nest_fors = self.parser.stack.count('for') - 1 # I am in stack already
        if nest_fors > 0:
            self.parser.code.add_line('forloop{} = forloop'.format(nest_fors))
        self.parser.code.add_line(
            'for forloop, {} in {}({}):'.format(
                parts[0].strip(),
                NodeFor.LIQUID_FORLOOP_CLASS,
                NodeExpression(self.parser)._parse(parts[1].strip())
            ),
            self.parser
        )
        self.parser.code.indent()

    @pop_stack
    def end(self):
        self.parser.code.dedent()
        nest_fors = self.parser.stack.count('for')
        if nest_fors > 0:
            self.parser.code.add_line('forloop = forloop{}'.format(nest_fors))

class NodeCycle(_Node):
    """Statement cycle {% cycle 1,2,3 %}"""

    @push_history
    def start(self, string):
        if not self.parser.stack or 'for' not in self.parser.stack:
            self.parser.raise_ex(
                "Statement {!r} must be in a for loop".format(self.name)
            )
        string = '({})'.format(string)
        self.parser.code.add_line(
            '{0}({1}[forloop.index0 % len({1})])'.format(
                LIQUID_COMPILED_RR_APPEND,
                string
            ),
            self.parser
        )

class NodeComment(_Node):
    """
    Node '{% comment ... %} {% endcomment %}'
    """

    LIQUID_COMMENTS = '_liquid_node_comments'

    @push_both
    def start(self, string):
        """Start to compile the node"""
        string = string or '#'
        self.prefix = string.split()
        if len(self.prefix) > 2:
            self.parser.raise_ex(
                'Comments can only be wrapped by no more than 2 strings'
            )
        self.parser.code.add_line(
            "{} = []".format(NodeComment.LIQUID_COMMENTS)
        )
        self.parser.code.add_line("{} = {}.append".format(
            LIQUID_COMPILED_RR_APPEND, NodeComment.LIQUID_COMMENTS))
        self.parser.code.add_line("{} = {}.extend".format(
            LIQUID_COMPILED_RR_EXTEND, NodeComment.LIQUID_COMMENTS))

    @pop_stack
    def end(self):
        """End node hit"""
        self.parser.code.add_line("{} = {}.append".format(
            LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
        self.parser.code.add_line("{} = {}.extend".format(
            LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))

        # merge broken lines, for example:
        # a {%if x%}
        # b
        # will be compiled as ['a '] ['\n', 'b']
        # without merging, comment sign will be insert after 'a '
        self.parser.code.add_line(
            '{0} = "".join({0}).splitlines(keepends = True)'.format(
                NodeComment.LIQUID_COMMENTS
            )
        )
        self.parser.code.add_line(
            'for comment in {}:'.format(NodeComment.LIQUID_COMMENTS)
        )
        self.parser.code.indent()
        self.parser.code.add_line('if comment.endswith("\\n"):')
        self.parser.code.indent()
        self.parser.code.add_line(
            '{}({!r} + comment[:-1].lstrip() + {!r} + "\\n")'.format(
                LIQUID_COMPILED_RR_APPEND,
                self.prefix[0] + ' ',
                (' ' + self.prefix[1]) if len(self.prefix) > 1 else ''
            )
        )
        self.parser.code.dedent()
        self.parser.code.add_line('else:')
        self.parser.code.indent()
        self.parser.code.add_line(
            '{}({!r} + comment.lstrip() + {!r})'.format(
                LIQUID_COMPILED_RR_APPEND,
                self.prefix[0] + ' ',
                (' ' + self.prefix[1]) if len(self.prefix) > 1 else ''
            )
        )
        self.parser.code.dedent()
        self.parser.code.dedent()

        self.parser.code.add_line(
            'del {}'.format(NodeComment.LIQUID_COMMENTS)
        )

class NodePython(_Node):
    """
    Node '{% python ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        self.parser.code.add_line(string, self.parser)

class NodeFrom(_Node):
    """
    Node '{% from ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        self.parser.code.add_line('from ' + string, self.parser)

class NodeImport(_Node):
    """
    Node '{% import ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        self.parser.code.add_line('import ' + string, self.parser)

class NodeUnless(_Node):
    """
    Node '{% unless %}'
    """
    @push_both
    def start(self, string):
        """Start to compile the node"""
        ifnode = NodeIf(self.parser)
        ifnode.start(string, prefix='if not (', suffix=')')
        ifnode.end()
        self.parser.code.indent()

class NodeCase(_Node):
    """
    Node '{% case ... %} {% endcase %}'
    """
    LIQUID_CASE_VARNAME = '_liquid_case_var'

    @push_both
    def start(self, string):
        """Start to compile the node"""
        self.parser.code.add_line(
            '{} = {}'.format(
                NodeCase.LIQUID_CASE_VARNAME,
                NodeExpression(self.parser)._parse(string)
            ),
            self.parser
        )

    @pop_stack
    def end(self):
        """End node hit"""
        self.parser.code.dedent()
        self.parser.code.add_line(
            'del {}'.format(NodeCase.LIQUID_CASE_VARNAME)
        )

class NodeWhen(_Node):
    """
    Node '{% when ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        if not self.parser.stack or self.parser.stack[-1] != 'case':
            self.parser.raise_ex('"when" must be in a "case" statement')
        ifelse = 'if' if self.parser.history[-1] == 'case' else 'elif'
        if self.parser.history[-1] == 'case':
            ifelse = 'if'
        else:
            ifelse = 'elif'
            self.parser.code.dedent()
        self.parser.code.add_line('{} {} == {}:'.format(
            ifelse, NodeCase.LIQUID_CASE_VARNAME, string), self.parser)
        self.parser.code.indent()

class NodeAssign(_Node):
    """
    Node '{% assign ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        parts = string.split('=', 1)
        if len(parts) == 1:
            self.parser.raise_ex(
                'Statement "assign" should be ' \
                'in format of "assign a, b = x | filter"'
            )
        variables = (part.strip() for part in parts[0].split(','))
        from . import _check_envs
        _check_envs({var:1 for var in variables})
        self.parser.code.add_line(
            '{} = {}'.format(
                parts[0].strip(),
                NodeExpression(self.parser)._parse(parts[1].strip())
            ),
            self.parser
        )

class NodeBreak(_Node):
    """
    Node '{% break %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        if string:
            self.parser.raise_ex(
                'Additional expressions for {!r}'.format(self.name)
            )
        if  not self.parser.stack or \
            not any(stack in ('for', 'while') for stack in self.parser.stack):
            self.parser.raise_ex(
                'Statement "{}" must be in a loop'.format(self.name)
            )
        self.parser.code.add_line(self.name, self.parser)

class NodeContinue(NodeBreak):
    """
    Node '{% continue %}'
    """

class NodeCapture(_Node):
    """
    Node '{% capture ... %} {% endcapture %}'
    """
    LIQUID_CAPTURES = '_liquid_captures'

    @push_both
    def start(self, string):
        """Start to compile the node"""
        from . import _check_envs
        _check_envs({string:1})

        self.variable = string # pylint:disable=attribute-defined-outside-init

        self.parser.code.add_line("{} = []".format(NodeCapture.LIQUID_CAPTURES))
        self.parser.code.add_line("{} = {}.append".format(
            LIQUID_COMPILED_RR_APPEND, NodeCapture.LIQUID_CAPTURES))
        self.parser.code.add_line("{} = {}.extend".format(
            LIQUID_COMPILED_RR_EXTEND, NodeCapture.LIQUID_CAPTURES))

    @pop_stack
    def end(self):
        """End node hit"""
        self.parser.code.add_line("{} = {}.append".format(
            LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
        self.parser.code.add_line("{} = {}.extend".format(
            LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))
        self.parser.code.add_line('{} = ("".join(str(x) for x in {}))'.format(
            self.variable, NodeCapture.LIQUID_CAPTURES))

class NodeIncrement(_Node):
    """
    Node '{% increment ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        if not string:
            self.parser.raise_ex(
                'No variable specified for {!r}'.format(self.name)
            )
        self.parser.code.add_line('{} += 1'.format(string), self.parser)

class NodeDecrement(_Node):
    """
    Node '{% decrement ... %}'
    """
    @push_history
    def start(self, string):
        """Start to compile the node"""
        if not string:
            self.parser.raise_ex(
                'No variable specified for {!r}'.format(self.name)
            )
        self.parser.code.add_line('{} -= 1'.format(string), self.parser)

class NodeWhile(NodeIf):
    """
    Node '{% while ... %} {% endwhile %}'
    """
    def start(self, string, prefix='while ', suffix=''):
        """Start to compile the node"""
        super().start(string, prefix, suffix)
