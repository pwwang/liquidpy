"""The top-level parser for liquid template"""
import re
import ast
from pathlib import Path
from functools import partial
from collections import deque, OrderedDict
from diot import Diot
from lark import v_args, Lark, Transformer
from lark.exceptions import VisitError as LarkVisitError
# load all shared tags
from . import tags # pylint: disable=unused-import
from .tagfrag import (
    TagFragVar,
    TagFragRange,
    TagFragGetAttr,
    TagFragGetItem,
    TagFragFilter,
    TagFragOutput,
    TagFragOpComparison,
)
from .tag import Tag, TagLiteral
from .tagmgr import get_tag
from .config import LIQUID_LOG_INDENT
from .exceptions import (
    TagUnclosed, EndTagUnexpected,
    TagWrongPosition
)

@v_args(inline=True)
class TagFactory(Transformer):
    # Last literal tag or last compact mode
    LAST_LITERAL_OR_COMPACT = None

    def __init__(self, parser, base_level=0):
        """Construct"""
        super().__init__()
        self.parser = parser
        self.config = parser.config
        self.stack = deque()
        self.base_level = base_level
        self.root = get_tag(
            'ROOT', None, self._context(Diot(line=1, column=1)
        ))
        if not isinstance(self.parser.template_name, Tag):
            self.config.logger.info('PARSING %s ...',
                                    self.parser.template_name)
            self.config.logger.info('-' * 40)

    def _ws_control(self, open_brace, close_brace):
        if not isinstance(self.LAST_LITERAL_OR_COMPACT, TagLiteral):
            return
        self.LAST_LITERAL_OR_COMPACT.RIGHT_COMPACT = "-" in open_brace
        self.LAST_LITERAL_OR_COMPACT = "-" in close_brace

    def _context(self, token):
        return Diot(parser=self.parser,
                    line=token.line,
                    column=token.column)

    def _starting_tag(self, tag):
        """Handle the relationships between tags when a tag is opening
        When the stack is empty, we treat the tag as direct tag (to ROOT),
        Then these tags will be rendered directly by ROOT tag (a virtual tag
        that deals with all direct child tags)
        If it is not empty, then that means this tag is a child of
        the last tag (parent) of the stack, we attach it to the children of the
        parent, and attach the parent to the parent of the child as well
        (useful to detect when a tag is inside the one that it is supposed to
        be. For exaple, `cycle` should be with `for` tag. Then we are able to
        trace back the parent to see if `for` is one of its parents)
        Also if VOID is False, meaning that this tag can have children, we
        need to push it into the stack.
        Another case we can do for the extended mode is that, we can allow
        tags to be both VOID and non-VOID.
        We can also do VOID = 'maybe' case. However, this type of tags can only
        have literals in it. When we hit the end tag of it, then we know it is
        a VOID = False tag. But before that, if we hit the other open tags,
        close tag of its parent or EOF then we know if it is a VOID = True tag,
        we need to move all the children of it to the upper level (its parent)
        For cases of set of tags appearing together, non-first tags should have
        PRIOR_TAGS and PARENT_TAGS defined, we need them to validate if the tag
        is in the right place or within the right parent. More than that,
        we also need the PRIOR_TAGS to prevent this tag to be treated as a
        child of its prior tags
        """
        if not self.stack:
            if tag._require_parents():
                raise TagWrongPosition(
                    f"Expecting parents {tag.PARENT_TAGS}: {tag}"
                )
            if tag._require_elders():
                raise TagWrongPosition(f'{tag} requires a prior tag.')

            tag.level = self.base_level
            if not isinstance(tag, TagLiteral):
                self.config.logger.info(
                    '%s%s',
                    LIQUID_LOG_INDENT * tag.level, tag
                )
            else:
                self.config.logger.debug(
                    '%s%s',
                    LIQUID_LOG_INDENT * tag.level, tag
                )
            self.root.children.append(tag)
        else:
            # assign siblings
            if tag._can_be_elder(self.stack[-1]):
                prev_tag = self.stack.pop()
                prev_tag.next = tag
                tag.prev = prev_tag

                tag.level = prev_tag.level

            # prior tags should not have VOID maybe, check?
            elif self.stack[-1].VOID == 'maybe':
                void_tag = self.stack.pop()
                void_tag.VOID = True
                if not void_tag.parent:
                    self.root.children.extend(void_tag.children)
                else:
                    void_tag.parent.children.extend(void_tag.children)

                del void_tag.children[:]

            if self.stack:
                self.stack[-1].children.append(tag)
                tag.parent = self.stack[-1]
                tag.level = tag.parent.level + 1

                if not isinstance(tag, TagLiteral):
                    self.config.logger.info('%s%s',
                                            LIQUID_LOG_INDENT * tag.level,
                                            tag)
                else:
                    self.config.logger.debug('%s%s',
                                             LIQUID_LOG_INDENT * tag.level,
                                             tag)

            # parent check
            # we need to do it after siblings assignment, because
            # direct parent could also valid from first sibling's
            # direct parent
            if not tag._parents_valid():
                raise TagWrongPosition(
                    f"Expecting parents {tag.PARENT_TAGS}: {tag}"
                )

        if not tag.VOID or tag.VOID == 'maybe':
            self.stack.append(tag)

    def var(self, data):
        return TagFragVar(data)

    def range(self, token):
        start, stop = token[1:-1].split('..', 1)
        try:
            start = int(start)
        except (TypeError, ValueError):
            start = TagFragVar(start)
        try:
            stop = int(stop)
        except (TypeError, ValueError):
            stop = TagFragVar(stop)
        return TagFragRange(start, stop)

    def getitem(self, obj, subscript):
        """The getitem operation"""
        return TagFragGetItem(obj, subscript)

    def getattr(self, obj, attr):
        """The getattr operation"""
        return TagFragGetAttr(obj, attr)

    def op_comparison(self, left, op, right):
        """The operator comparisons"""
        return TagFragOpComparison(left, op, right)

    def logical(self, expr, *op_expr):
        """liquid does not have a good support precedence of and / or
        if we have more than 3 operators
        however, with 3 operators, and has higher precedence
        see:
        https://shopify.github.io/liquid/basics/operators/#order-of-operations
        """
        len_op_expr = len(op_expr) // 2
        if len_op_expr == 1:
            return TagFragOpComparison(expr, *op_expr)
        if len_op_expr == 2: # 0,1,2,3
            # "and" have precedence
            if op_expr[2] == 'and':
                return TagFragOpComparison(
                    expr, op_expr[0],
                    TagFragOpComparison(*op_expr[1:])
                )
            return TagFragOpComparison(
                TagFragOpComparison(expr, *op_expr[:2]),
                *op_expr[2:]
            )
        else:
            # Start from the right most
            # expr (op_expr) (op_expr) (op_expr)
            # true (or false) (or false) (or true)
            # (true or) (false or) (false or) true
            op_expr = list(reversed(op_expr))
            op_expr.append(expr)
            expr = op_expr.pop(0)
            # true (or false) (or false) (or true)

            opc = TagFragOpComparison(op_expr[1], op_expr[0], expr)
            for i in range(1, len_op_expr):
                op = op_expr[2*i]
                expr = op_expr[2*i+1]
                opc = TagFragOpComparison(expr, op, opc)
            return opc

    def filter(self, filtername):
        """Rule filter"""
        return TagFragFilter(filtername)

    def filter_args(self, *exprs):
        """Rule filter_args"""
        return exprs

    def expr_filter(self, filtername, filter_args=None):
        """Rule expr_filter"""
        # TagFragFilter, (arg1, arg2, ...)
        return (filtername, filter_args or ())

    def output(self, expr, *expr_filters):
        """Rule output {{ }} """
        return TagFragOutput(expr, expr_filters)

    def raw_tag(self, raw):
        match = re.match(
            r'^(\{%-?)\s*raw\s*(-?%\})([\s\S]*?)(\{%-?)\s*end\s*raw\s*(-?%\})',
            raw
        )
        open_brace1 = match.group(1)
        close_brace1 = match.group(2)
        content = match.group(3)
        open_brace2 = match.group(4)
        close_brace2 = match.group(5)

        self._ws_control(open_brace1, close_brace2)
        if '-' in close_brace1:
            content = content.lstrip()
        if '-' in open_brace2:
            content = content.rstrip()
        tag = get_tag('RAW', content, self._context(raw))
        self._starting_tag(tag)
        return tag

    def start_tag(self, open_brace, inner, close_brace):
        self._ws_control(open_brace, close_brace)
        # inner is already transformed into a tag
        # is it enough to point to the tag itself or
        # we need to point to the fragments as well
        inner.context = self._context(open_brace)
        self._starting_tag(inner)
        return inner

    def end_tag(self, open_brace, tagname, close_brace):
        """Handle tag relationships when closing a tag."""
        self._ws_control(open_brace, close_brace)

        tagname = str(tagname)
        if not self.stack:
            raise EndTagUnexpected(tagname)

        last_tag = self.stack.pop()
        if last_tag.name == tagname:
            # collapse VOID to False for maybe VOID tags
            if last_tag.VOID == 'maybe':
                self.config.logger.debug(
                    '    Collapsing tag (VOID: maybe -> False): %s', last_tag
                )
                last_tag.VOID = False
            self.config.logger.info('%s<EndTag(name=end%s, line=%s, col=%s)>',
                                    LIQUID_LOG_INDENT * last_tag.level,
                                    last_tag.name,
                                    open_brace.line,
                                    open_brace.column)
        elif last_tag.parent and last_tag.parent.name == tagname:
            assert last_tag.parent is self.stack[-1]
            self.stack.pop()
            self.config.logger.info('%s<EndTag(name=end%s, line=%s, col=%s)>',
                                    LIQUID_LOG_INDENT * last_tag.parent.level,
                                    last_tag.parent.name,
                                    open_brace.line,
                                    open_brace.column)
            # we have to check if children of last_tag's parent have been closed
            # in other words, last_tag's siblings
            eldest = last_tag._eldest()
            # of course it is not VOID
            # If a tag needs parent, supposingly, the parent will close
            # for it
            if eldest and not eldest._require_parents():
                raise TagUnclosed(
                    eldest._format_error(eldest)
                )
        else:
            # now we tried to
            # 1) close the direct tag (last_tag) or
            # 2) the parent of the last_tag
            # However, for 2) we need to check if the tags inside the parent
            # tag have been closed
            # In the case of
            #
            # {% for ... %}
            #     {% if ... %}
            # {% endfor %}
            #
            # "endfor" will close "for ...", but "if ..."
            # remains unclosed
            #
            # if last_tag has siblings, we check the most prior one
            eldest = last_tag._eldest()
            if eldest:
                if eldest.name == tagname:
                    # nothing to do, since it's not in the stack already
                    self.config.logger.info(
                        '%s<EndTag(name=end%s)>',
                        LIQUID_LOG_INDENT * eldest.level,
                        tagname
                    )
                # if it has to be closed
                elif not eldest._require_parents():
                    raise TagUnclosed(
                        eldest._format_error(eldest)
                    )
            # if last_tag doesn't have first sibling
            # check itself
            elif not last_tag._require_parents():
                raise TagUnclosed(
                    last_tag._format_error(last_tag)
                )
            else:
                raise EndTagUnexpected(
                    Tag._format_error(Diot(context=self._context(open_brace)))
                )


    def output_tag(self, open_brace, output, close_brace):
        self._ws_control(open_brace, close_brace)
        tag = get_tag('OUTPUT', output, self._context(open_brace))
        self._starting_tag(tag)
        return tag

    def literal_tag(self, literal):
        tag = get_tag('LITERAL', literal, self._context(literal))
        if self.LAST_LITERAL_OR_COMPACT is True:
            tag.LEFT_COMPACT = True
        self.LAST_LITERAL_OR_COMPACT = tag
        self._starting_tag(tag)
        return tag

    def start(self, *tags):
        return self.root

    int = number = string = lambda _, data: ast.literal_eval(str(data))
    nil = lambda _: None
    true = lambda _: True
    false = lambda _: False
    contains = op_comparison
    expr_nological = expr = tag = inner_tag = lambda _, data: data
    literal_start_tag = literal_tag

class Parser:
    """The parser object to parse the whole template

    Attributes:
        GRAMMAR (str): The lark grammar for the whole template
        TRANSFORMER (lark.Transformer): The transformer to
            transform the trees/tokens
    """
    GRAMMAR = TRANSFORMER = None

    def __init__(self, config):
        self.config = config
        self.template_name = self.template = None

    def parse(self, template_string, template_name):
        """Parse the template string

        Args:
            template_string (str): The template string
            template_name (str): The template name, used in exceptions
        Returns:
            TagRoot: The TagRoot object, allowing later rendering
                the template with envs/context
        """
        self.template = template_string.splitlines()
        self.template_name = template_name
        cachefile = str(Path(__file__).parent.joinpath(
            f"{self.__class__.__name__}.larkcache"
        ))
        if self.config.debug:
            cachefile = False

        self.config.logger.debug('COMPILED GRAMMAR')
        self.config.logger.debug('-' * 40)
        grammar = str(self.GRAMMAR)
        for gline in grammar.splitlines():
            if not gline:
                continue
            self.config.logger.debug(gline)
        self.config.logger.debug('')

        return Lark(grammar,
                    parser='lalr',
                    start='start',
                    debug=False,
                    maybe_placeholders=True,
                    transformer=self.TRANSFORMER(self),
                    cache=cachefile).parse(template_string)

    def get_context(self, lineno, contexts=10):
        # [1,2,...9]
        # line = 8, pre_/post_lines = 5
        # should show: 3,4,5,6,7, 8, 9
        pre_lines = post_lines = contexts // 2
        pre_lineno = max(1, lineno - pre_lines) # 3
        post_lineno = min(len(self.template), lineno + post_lines) # 9
        return OrderedDict(zip(
            range(pre_lineno, post_lineno+1),
            self.template[(pre_lineno-1):post_lineno]
        ))
