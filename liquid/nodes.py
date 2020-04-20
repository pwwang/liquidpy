"""Nodes in liquidpy"""
import logging
import warnings
from functools import partial
from contextlib import suppress
from pathlib import Path
import attr
from .defaults import (LIQUID_RENDERED_EXTEND, LIQUID_RENDERED_APPEND,
                       LIQUID_NODES, LIQUID_RENDERED,
                       LIQUID_LOGLEVELID_DETAIL, LIQUID_LOGGER_NAME)
from .code import LiquidCode
from .stream import safe_split
from .exceptions import (LiquidSyntaxError, LiquidCodeTagExists,
                         LiquidNodeAlreadyRegistered)
LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)
# pylint: disable=no-value-for-parameter,fixme
def register_node(name, klass):
    """@API
    Register a new node
    To unregister a node:
    ```
    from liquid.defaults import LIQUID_NODES
    del LIQUID_NODES[<name>]
    ```
    @params:
        name (string): The name of the node, will be match at `{% <name> ...`
        klass (type): The class the handle the nodes"""
    if name in LIQUID_NODES:
        raise LiquidNodeAlreadyRegistered(f"Node {name!r} has already "
                                          "been registered")
    LIQUID_NODES[name] = klass

def compact(string, left, right):
    """@API
    Apply compact mode to the string
    @params:
        string (str): The string to apply compact mode
        left (bool): If the left side of the string should be compacted
        right (bool): If the right side of the string should be compacted
    @returns:
        (str): The string with compact mode applied"""
    if left:
        string = string.lstrip(" \t").lstrip('\n')
    if right:
        string = string.rstrip(" \t").rstrip('\n')
    return string

def parse_mixed(mixed, shared_code):
    """@API
    Parse mixed expressions like 1 + `a | @plus: 1`
    @params:
        mixed (str): The mixed expression to be parsed
        shared_code (LiquidCode): A LiquidCode object needed
            by `NodeLiquidExpression`
    @returns:
        (str): The parsed expression"""
    from .expression import NodeLiquidExpression
    # safely split by backticks
    mixed = safe_split(mixed, '`', quotes="\"'", trim=False)
    if len(mixed) % 2 == 0:
        raise LiquidSyntaxError('Unclosed liquid expression')
    liquid_expr = False
    ret = ''
    for part in mixed:
        if part and liquid_expr:
            expr_node = NodeLiquidExpression(attrs=part,
                                             shared_code=shared_code)
            expr_node.start()
            ret += expr_node._parse()
        elif part:
            ret += part
        liquid_expr = not liquid_expr
    return f"({ret})"

def check_quotes(value):
    """@API
    Check if value is correctly quoted or not quoted:
    True: <empty string>
    True: <unquoted string>
    False: 'abc <compond quote>
    False: "abc <compond quote>
    False: "abc' <compond quote>
    False: 'abc" <compond quote>
    @params:
        value (string): The value to check
    @returns:
        (bool): True if value is correctly quoted otherwise False"""
    if len(value) == 1 and value in ('"', '\''):
        return False
    if ((value[:1] in ('"', '\'') or value[-1:] in ('"', '\'')) and
            value[:1] != value[-1:]):
        return False
    return True

def unquote(value):
    """@API
    Remove quotes from a string
    Assuming it's checked by check_quotes
    @params:
        value (str): The value to be unquoted
    @returns:
        (str): The unquoted value"""
    return value[1:-1] if value[:1] in ('"', '\'') else value

def scan_file(relpath, dirs, reverse=True):
    """@API
    Scan a file in the dirs
    @params:
        relpath (str): The relative path
        dirs (list): The list of directories to scan
        reverse (bool): Scan the last directory in the list first?
    @returns:
        (Path): The file found in the `dirs`"""
    relpath = Path(relpath)
    if relpath.is_absolute():
        return relpath
    if reverse:
        dirs = reversed(dirs)
    for directory in dirs:
        path = directory.joinpath(relpath)
        if path.is_file():
            return path
    return None

@attr.s(kw_only=True)
class NodeVoid:
    """@API
    Nodes without ending/closing
    For example: {% config mode="compact" include="xxx" %}
    @params:
        name (str): The name of the node, will be matched at `{% <name>`
        attrs (str): The rest string of the node other than name
        code (LiquidCode): The LiquidCode object to save the codes
        shared_code (LiquidCode): The LiquidCode object to save some
            shared codes
        config (LiquidConfig): The LiquidConfig object with the configurations
        context (diot.Diot): The context of this node"""
    # The name of the node
    name = attr.ib()
    # mode="compact" include="xxx"
    attrs = attr.ib()
    # the code object
    code = attr.ib(repr=False, eq=False)
    # the shared code object
    shared_code = attr.ib(repr=False, eq=False)
    # the configuration
    config = attr.ib(default=None, repr=False, eq=False)
    # the context, including filename, lineno, history, and stacks
    context = attr.ib(default=None, repr=False, eq=False)
    def __attrs_post_init__(self):
        if self.context:
            LOGGER.debug("[PARSER%2s] - Found node %r at %s:%s",
                         self.context.nstack, self.name,
                         self.context.filename, self.context.lineno)
    def start(self):
        """@API
        Node hit. Start validating the node and preparing for parsing"""

    def try_mixed(self, mixed):
        """@API
        Try to parse mixed expression using my shared_code
        @params:
            mixed (str): The mixed expression to be parsed
        @returns:
            (str): The parsed expression"""
        try:
            return parse_mixed(mixed, self.shared_code)
        except LiquidSyntaxError as lse:
            raise LiquidSyntaxError(str(lse), self.context) from lse

    def parse_node(self):
        """@API
        Parse the node into python codes, and add them to `self.code`
        for execution"""
        if self.context:
            LOGGER.debug("[PARSER%2s]   Parsing node %r at %s:%s",
                         self.context.nstack, self.name,
                         self.context.filename, self.context.lineno)
            self.context.history.append(self)

@attr.s(kw_only=True)
class Node(NodeVoid):
    """@API
    Nodes need to be closed
    For example: {% if ... %} ... {% endif %}"""
    def parse_node(self):
        """@API
        Returns False to parse content as literal
        Otherwise as normal liquid template"""
        super().parse_node()
        self.context.stacks.append(self)

    def end(self, name):
        """@API
        End the node, check if I am the right end node to close."""
        last_node = self.context.stacks.pop(-1)
        if last_node.name != name:
            raise LiquidSyntaxError(f"Unmatched closing node 'end{name}' "
                                    f"for {last_node.name!r}", self.context)

@attr.s(kw_only=True)
class NodeIntact(Node):
    """@API
    Content intact node, where the content remains
    unparsed as liquid template.
    The content is grabbed between {% raw %} and {% endraw %}, which
    will then be parsed in parse_content
    @params:
        content (str): The content between open and close node
        lineno (int): The line number when the node hit, as `context.lineno`
            will be changed during further parsing
        compact_left (bool): Whether the left side of `content` should
            be compact
        compact_right (bool): Whether the right side of `content` should
            be compact"""
    # we should grab content between open and close node
    content = attr.ib(default=None, init=False, eq=False, repr=False)
    # line number may be changed if parse is deferred
    lineno = attr.ib(default=1, init=False, repr=False)
    # should do compact on left of content?
    compact_left = attr.ib(default=False, init=False, eq=False, repr=False)
    # should do compact on right of content?
    compact_right = attr.ib(default=False, init=False, eq=False, repr=False)
    def parse_content(self):
        """@API
        Add debug information that I am parsing the content"""
        if self.context:
            LOGGER.debug("[PARSER%2s] - Parsing content of %snode %r at %s:%s",
                         self.context.nstack,
                         (f"deferred({self.defer}) "
                          if hasattr(self, "defer") else ""),
                         self.name, self.context.filename, self.context.lineno)

@attr.s(kw_only=True)
class NodeLiquidLiteral(NodeVoid):
    """@API
    Any literals in the template"""
    name = attr.ib(default='<liquid_literal>')
    def parse_node(self):
        super().parse_node()
        if not self.attrs:
            return
        lines = self.attrs.splitlines(keepends=True)
        if len(lines) > 1:
            self.code.add_line(f"{LIQUID_RENDERED_EXTEND}([")
            self.code.indent()
            for line in lines:
                self.code.add_line(repr(line) + ',', self.context)
            self.code.dedent()
            self.code.add_line("])")
        else:
            self.code.add_line(f"{LIQUID_RENDERED_APPEND}({lines[0]!r})",
                               self.context)

@attr.s(kw_only=True)
class NodeLiquidComment(NodeVoid):
    """@API
    Node like {# ... #}"""
    name = attr.ib(default='<liquid_comment>')
    shared_code = attr.ib(default=None)
    code = attr.ib(default=None)
    config = attr.ib(default=None)
    attrs = attr.ib(default='')

class NodeConfig(NodeVoid):
    """@API
    Node {% config mode="compact" include=".." loglevel="info" %}"""
    def start(self):
        configs = safe_split(self.attrs, ',')
        if not all(configs):
            raise LiquidSyntaxError("Empty configs found.", self.context)
        self.attrs = {}
        for config in configs:
            parts = safe_split(config, '=')
            if len(parts) != 2:
                raise LiquidSyntaxError("Wrong format config [%s], "
                                        "expect 'key=\"value\"'" % config,
                                        self.context)
            if not check_quotes(parts[1]):
                raise LiquidSyntaxError("Unclosed string in config: "
                                        f"{config}", self.context)
            self.attrs[parts[0]] = unquote(parts[1])

    def parse_node(self):
        super().parse_node()
        for key, val in self.attrs.items():
            self.config.__setattr__(key, val)

class NodeIf(Node):
    """@API
    Node {% if ... %} ... {% endif %}"""
    def start(self):
        # allow statement to end with ':'
        self.attrs = self.attrs.rstrip(':')
        if not self.attrs:
            raise LiquidSyntaxError(f"No expressions for {self.name!r} node",
                                    self.context)
    def parse_node(self):
        super().parse_node()
        self.code.add_line(f"{self.name} {self.try_mixed(self.attrs)}:",
                           self.context)
        self.code.indent()

    def end(self, name):
        super().end(name)
        # we need to add "pass" to support
        # {% if 1 %}{% endif %}
        if self.context.history[-1] is self:
            self.code.add_line("pass")
        self.code.dedent()

NodeWhile = NodeIf

class NodeElse(NodeVoid):
    """@API
    Node {% else %}"""
    def start(self):
        # allow statement to end with ':'
        self.attrs = self.attrs.rstrip(':')
        if self.attrs and self.attrs.split()[0] != "if":
            raise LiquidSyntaxError("No expressions allowed for 'else' node",
                                    self.context)
        if (not self.context.stacks or
                self.context.stacks[-1].name not in ('case', 'if', 'unless')):
            raise LiquidSyntaxError("'else' must be in an "
                                    "'if/unless/case' node", self.context)
        if self.attrs == "if":
            raise LiquidSyntaxError("No expressions for 'else if' node",
                                    self.context)
        # if no statement found after if/unless
        # so that following is supported
        # {% if True %}{%else%} something else {% endif %}
        if (self.context.history and
                isinstance(self.context.history[-1], (NodeIf, NodeUnless))):
            self.code.add_line('pass')

    def parse_node(self):
        super().parse_node()
        self.code.dedent()
        if not self.attrs:
            self.code.add_line('else:', self.context)
            self.code.indent()
        else: # else if
            # we con't need to close this
            self.context.stacks.pop(-1)
            NodeIf(name="if", code=self.code, shared_code=self.shared_code,
                   context=self.context, config=self.config,
                   attrs=self.attrs.split(maxsplit=1)[1]).parse_node()

class NodeElseif(NodeVoid):
    """@API
    Node {% elseif .. %}, {% elif .. %} and {% elsif ... %}"""
    def start(self):
        self.attrs = self.attrs.rstrip(':')
        if not self.attrs:
            raise LiquidSyntaxError(f"No expressions for {self.name!r} node",
                                    self.context)
        if (not self.context.stacks or not isinstance(
                self.context.stacks[-1], (NodeIf, NodeCase, NodeUnless)
        )):
            raise LiquidSyntaxError(f"{self.name!r} must be in an "
                                    "'if/unless/case' node", self.context)
        # if no statement found after if
        if (self.context.history and
                isinstance(self.context.history[-1], NodeIf)):
            self.code.add_line('pass')
        self.code.dedent()

    def parse_node(self):
        super().parse_node()
        source = 'elif ' + self.try_mixed(self.attrs)
        self.code.add_line(source + ':', self.context)
        self.code.indent()

class NodeRaw(NodeIntact):
    """@API
    Node {% raw %} ... {% endraw %}"""
    def start(self):
        if self.attrs:
            raise LiquidSyntaxError("No expressions allowed for 'raw' node",
                                    self.context)
    def parse_content(self):
        super().parse_content()
        content = compact(self.content, self.compact_left, self.compact_right)
        NodeLiquidLiteral(attrs=content, code=self.code,
                          shared_code=self.shared_code,
                          context=self.context).parse_node()

class NodeFor(Node):
    """@API
    Node '{% for ... %} {% endfor %}'"""
    LIQUID_FORLOOP_CLASS = '_Liquid_forloop_class'
    def start(self):
        self.attrs = self.attrs.rstrip(':')
        parts = safe_split(self.attrs, ' in ', limit=1)
        if len(parts) < 2:
            raise LiquidSyntaxError("'for' node expects format: "
                                    "'for var1, var2 in expr'", self.context)

    def parse_node(self): #pylint: disable=too-many-statements
        super().parse_node()
        with suppress(LiquidCodeTagExists), \
                self.shared_code.tag(NodeFor.LIQUID_FORLOOP_CLASS) as tagged:
            tagged.add_line('')
            tagged.add_line(f'class {NodeFor.LIQUID_FORLOOP_CLASS}:')
            tagged.indent()
            tagged.add_line('"""Enabled forloop object in original liquid"""')
            tagged.add_line('def __init__(self, iterable):')
            tagged.indent()
            tagged.add_line('self._iterable = [it for it in iterable]')
            tagged.add_line('self.index0 = -1')
            tagged.add_line('self.length = len(self._iterable)')
            tagged.dedent()
            tagged.add_line('@property')
            tagged.add_line('def first(self):')
            tagged.indent()
            tagged.add_line('return self.index0 == 0')
            tagged.dedent()
            tagged.add_line('@property')
            tagged.add_line('def last(self):')
            tagged.indent()
            tagged.add_line('return self.index == self.length')
            tagged.dedent()
            tagged.add_line('@property')
            tagged.add_line('def index(self):')
            tagged.indent()
            tagged.add_line('return self.index0 + 1')
            tagged.dedent()
            tagged.add_line('@property')
            tagged.add_line('def rindex(self):')
            tagged.indent()
            tagged.add_line('return self.length - self.index0')
            tagged.dedent()
            tagged.add_line('@property')
            tagged.add_line('def rindex0(self):')
            tagged.indent()
            tagged.add_line('return self.rindex - 1')
            tagged.dedent()
            tagged.add_line('def __iter__(self):')
            tagged.indent()
            tagged.add_line('return self')
            tagged.dedent()
            tagged.add_line('def __next__(self):')
            tagged.indent()
            tagged.add_line('self.index0 += 1')
            tagged.add_line('if self.index > self.length:')
            tagged.indent()
            tagged.add_line('raise StopIteration')
            tagged.dedent()
            tagged.add_line('ret = [self]')
            tagged.add_line('if isinstance(self._iterable'
                            '[self.index0], (list, tuple)):')
            tagged.indent()
            tagged.add_line('ret.extend(self._iterable[self.index0])')
            tagged.dedent()
            tagged.add_line('else:')
            tagged.indent()
            tagged.add_line('ret.append(self._iterable[self.index0])')
            tagged.dedent()
            tagged.add_line('return ret')
            tagged.dedent()
            tagged.dedent()
        # I am in stack already
        nest_fors = len([node for node in self.context.stacks
                         if isinstance(node, NodeFor)]) - 1
        if nest_fors > 0:
            # save my forloop object to avoid being overridden by inner ones
            self.code.add_line(f'forloop{nest_fors} = forloop')
        parts = safe_split(self.attrs, ' in ')
        # allow: for a, b in a + `1 | @increment`
        parts[1] = self.try_mixed(parts[1])
        self.code.add_line(
            f'for forloop, {parts[0]} in '
            f'{NodeFor.LIQUID_FORLOOP_CLASS}({parts[1]}):',
            self.context
        )
        self.code.indent()

    def end(self, name):
        super().end(name)
        nest_fors = len([node for node in self.context.stacks
                         if isinstance(node, NodeFor)])
        if nest_fors > 0:
            # recover my forloop object
            self.code.add_line('forloop = forloop{}'.format(nest_fors))
        self.code.dedent()

class NodeCycle(NodeVoid):
    """@API
    Node {% cycle ... %}"""
    def start(self):
        if not any(isinstance(node, (NodeWhile, NodeFor))
                   for node in self.context.stacks):
            raise LiquidSyntaxError("'cycle' node must be in a "
                                    "'for/while' loop", self.context)

    def parse_node(self):
        super().parse_node()
        varname = f"_for_cycle_{id(self)}"
        self.code.add_line(f"{varname} = ({self.attrs})")
        self.code.add_line(f"{LIQUID_RENDERED_APPEND}"
                           f"({varname}[forloop.index0 % len({varname})])",
                           self.context)

@attr.s(kw_only=True)
class NodeComment(Node):
    """@API
    Node {% comment ... %} ... {% endcomment %}"""
    LIQUID_COMMENT_PREFIX = '_liquid_comment'
    LIQUID_COMMENT_LINE_FORMATTER = '_liquid_comment_line_formatter'
    def start(self):
        self.attrs = self.attrs or '#'
        if len(self.attrs.split()) > 2:
            raise LiquidSyntaxError("Comments can only be wrapped by "
                                    "no more than 2 strings", self.context)
        self.attrs = self.attrs.split()
        if len(self.attrs) == 1:
            self.attrs.append('')

    def parse_node(self):
        super().parse_node()
        with suppress(LiquidCodeTagExists), self.shared_code.tag(
                NodeComment.LIQUID_COMMENT_LINE_FORMATTER
        ) as tagged:
            tagged.add_line(f"def {NodeComment.LIQUID_COMMENT_LINE_FORMATTER}"
                            f"(comline, prefix1, prefix2):")
            tagged.indent()
            tagged.add_line("prefix2 = prefix2 and ' ' + prefix2")
            tagged.add_line("line, end = comline, ''")
            tagged.add_line("if line[-1:] == '\\n':")
            tagged.indent()
            tagged.add_line("line = line[:-1]")
            tagged.add_line("end = '\\n'")
            tagged.dedent()
            tagged.add_line("return f'{prefix1} {line}{prefix2}{end}'")
            tagged.dedent()
        comcode = LiquidCode()
        self.context.parser.code.add_code(comcode)
        com_listname = f"{NodeComment.LIQUID_COMMENT_PREFIX}_{id(self)}"
        comcode.add_line("")
        comcode.add_line(f"# NODE COMMENT: {id(self)}")
        comcode.add_line(f"{com_listname} = []")

        comcode.add_line(f"{LIQUID_RENDERED_APPEND} = "
                         f"{com_listname}.append")
        comcode.add_line(f"{LIQUID_RENDERED_EXTEND} = "
                         f"{com_listname}.extend")
        self.context.parser.code = comcode

    def end(self, name):
        super().end(name)
        com_listname = f"{NodeComment.LIQUID_COMMENT_PREFIX}_{id(self)}"
        comcode = self.context.parser.code
        # resume append and extend
        comcode.add_line(f"{LIQUID_RENDERED_APPEND} = "
                         f"{LIQUID_RENDERED}.append")
        comcode.add_line(f"{LIQUID_RENDERED_EXTEND} = "
                         f"{LIQUID_RENDERED}.extend")
        # add the comment
        comcode.add_line(f"{LIQUID_RENDERED_EXTEND}(")
        comcode.indent()
        comcode.add_line(f"{NodeComment.LIQUID_COMMENT_LINE_FORMATTER}(_, "
                         f"{self.attrs[0]!r}, {self.attrs[1]!r})")
        comcode.add_line(f"for _ in ''.join({com_listname}).splitlines("
                         "keepends=True)")
        comcode.dedent()
        comcode.add_line(")")
        comcode.add_line(f"del {com_listname}")
        comcode.add_line("# NODE COMMENT END")
        comcode.add_line("")
        # resume the parser's code
        self.context.parser.code = self.code

class NodeBreak(NodeVoid):
    """@API
    Node {% break %}"""
    def start(self):
        if self.attrs:
            raise LiquidSyntaxError("No expressions allowed for "
                                    f"{self.name!r}", self.context)
        if not any(isinstance(node, (NodeFor, NodeWhile))
                   for node in self.context.stacks):
            raise LiquidSyntaxError(f"{self.name!r} node must be in a "
                                    "'for/while' loop", self.context)

    def parse_node(self):
        super().parse_node()
        self.code.add_line(self.name, self.context)
NodeContinue = NodeBreak

class NodeAssign(NodeVoid):
    """@API
    Node like {% assign a = `1 | @plus: 1` %}"""
    def start(self):
        parts = self.attrs.split('=', 1)
        if len(parts) < 2:
            raise LiquidSyntaxError(f"Malformat {self.name!r} node, "
                                    "expect 'assign a, b = 1 + `2 "
                                    "| @plus: 1`'", self.context)

    def parse_node(self):
        super().parse_node()
        parts = self.attrs.split('=', 1)
        values = self.try_mixed(parts[1].strip())
        self.code.add_line(f"{parts[0].strip()} = {values}", self.context)

class NodeCapture(Node):
    """@API
    Node like {% capture x %} ... {% endcapture %}"""
    LIQUID_CAPTURE_PREFIX = '_liquid_capture'
    def start(self):
        if not self.attrs.isidentifier():
            raise LiquidSyntaxError("Not a valid variable name "
                                    f"{self.attrs!r} for {self.name!r} node",
                                    self.context)

    def parse_node(self):
        """@API
        Start a new code to save the content generated in the content"""
        super().parse_node()
        capcode = LiquidCode()
        self.context.parser.code.add_code(capcode)
        capture_listname = f"{NodeCapture.LIQUID_CAPTURE_PREFIX}_{id(self)}"
        capcode.add_line("")
        capcode.add_line(f"# NODE CAPTURE: {id(self)}")
        capcode.add_line(f"{capture_listname} = []")
        # replace append and extend function to make node inside add
        # content to the capture list
        capcode.add_line(f"{LIQUID_RENDERED_APPEND} = "
                         f"{capture_listname}.append")
        capcode.add_line(f"{LIQUID_RENDERED_EXTEND} = "
                         f"{capture_listname}.extend")
        # use the capcode for inside nodes
        self.context.parser.code = capcode

    def end(self, name):
        super().end(name)
        capture_listname = f"{NodeCapture.LIQUID_CAPTURE_PREFIX}_{id(self)}"
        self.context.parser.code.add_line(f"{self.attrs} = ''.join(str(_) "
                                          f"for _ in {capture_listname})")
        self.context.parser.code.add_line(f"del {capture_listname}")
        # resume append and extend
        self.context.parser.code.add_line(f"{LIQUID_RENDERED_APPEND} = "
                                          f"{LIQUID_RENDERED}.append")
        self.context.parser.code.add_line(f"{LIQUID_RENDERED_EXTEND} = "
                                          f"{LIQUID_RENDERED}.extend")
        self.context.parser.code.add_line("# NODE CAPTURE END")
        self.context.parser.code.add_line("")
        # resume the parser's code
        self.context.parser.code = self.code

@attr.s(kw_only=True)
class NodeCase(Node):
    """@API
    Node like {% case x %} ... {% endcase %}"""
    varname = attr.ib(default='', init=False, repr=False, eq=False)
    # when the first when hit, should use if, otherwise elif
    first_when = attr.ib(default=True, init=False, repr=False, eq=False)
    def start(self):
        if not self.attrs:
            raise LiquidSyntaxError(f"No values found for {self.name!r} node",
                                    self.context)

    def parse_node(self):
        super().parse_node()
        self.varname = f"_case_{id(self)}"
        value = self.try_mixed(self.attrs)
        self.code.add_line(f"{self.varname} = {value}", self.context)

    def end(self, name):
        super().end(name)
        if self.first_when:
            raise LiquidSyntaxError(f"No 'when' node found in {self.name!r}")
        self.code.dedent()

class NodeWhen(NodeVoid):
    """@API
    Node {% when ... %} in case"""
    def start(self):
        if not self.attrs:
            raise LiquidSyntaxError(f"No values found for {self.name!r} node",
                                    self.context)
        if (not self.context.stacks or
                not isinstance(self.context.stacks[-1], NodeCase)):
            raise LiquidSyntaxError(f"{self.name!r} node must be in a "
                                    "'case' node", self.context)

    def parse_node(self):
        super().parse_node()
        varname = self.context.stacks[-1].varname
        value = self.try_mixed(self.attrs)
        equal = f"{varname} == {value}"
        if self.context.stacks[-1].first_when:
            self.code.add_line(f"if {equal}:", self.context)
            self.context.stacks[-1].first_when = False
        else:
            self.code.dedent()
            self.code.add_line(f"elif {equal}:", self.context)
        self.code.indent()

class NodeIncrement(NodeVoid):
    """@API
    Node like {% increment x %}"""
    def start(self):
        if not self.attrs:
            raise LiquidSyntaxError("No variable specified for "
                                    f"{self.name!r} node", self.context)
        if not self.attrs.isidentifier():
            raise LiquidSyntaxError(f"Invalid variable name {self.attrs!r} "
                                    f"for {self.name!r} node", self.context)

    def parse_node(self):
        super().parse_node()
        self.code.add_line(f"{self.attrs} += 1", self.context)

class NodeDecrement(NodeIncrement):
    """@API
    Node like {% increment y %}"""
    def parse_node(self):
        NodeVoid.parse_node(self)
        self.code.add_line(f"{self.attrs} -= 1", self.context)

class NodeFrom(NodeVoid):
    """@API
    Node {% from ... import ... %}"""
    def start(self):
        # pylint: disable=unsupported-membership-test
        if ' import ' not in self.attrs:
            raise LiquidSyntaxError("Expect 'from ... import ...' in "
                                    f"{self.name!r} node", self.context)

    def parse_node(self):
        super().parse_node()
        self.code.add_line(f"from {self.attrs}", self.context)

class NodeImport(NodeVoid):
    """@API
    Node {% import ... %}"""
    def parse_node(self):
        super().parse_node()
        self.code.add_line(f"import {self.attrs}", self.context)

class NodePython(Node):
    """@API
    Node like {% python a = 1 %} and {% python %}a = 1{% endpython %}"""
    def parse_node(self):
        super().parse_node()
        if self.attrs:
            # it should be void, pop out of the stack
            self.context.stacks.pop(-1)
            self.code.add_line(self.attrs, self.context)
            return None
        ret = NodeIntact(name=self.name, attrs='', code=self.code,
                         shared_code=self.shared_code, config=self.config,
                         context=self.context)
        ret.parse_content = partial(NodePython.parse_content, ret)
        return ret

    def parse_content(self):
        """@API
        Parse the content between {% python %} and {% endpython %}"""
        NodeIntact.parse_content(self)
        content = compact(self.content, self.compact_left, self.compact_right)
        for line in content.splitlines():
            self.code.add_line(line, self.context)

class NodeUnless(Node):
    """@API
    Node like {% unless x %} ... {% endunless %}"""
    def start(self):
        self.attrs = self.attrs.rstrip(':')
        if not self.attrs:
            raise LiquidSyntaxError("No expressions found for "
                                    f"{self.name!r} node", self.context)

    def parse_node(self):
        super().parse_node()
        self.code.add_line(f"if not ({self.try_mixed(self.attrs)}):",
                           self.context)
        self.code.indent()

    def end(self, name):
        super().end(name)
        self.code.dedent()

@attr.s(kw_only=True)
class NodeInclude(NodeVoid):
    """@API
    Node {% include ... %}"""
    incfile = attr.ib(default=None, init=False)
    vars = attr.ib(default=attr.Factory(dict), init=False)
    LIQUID_INCLUDE_SOURCE = '_liquid_include_source'
    def start(self):
        if not self.attrs:
            raise LiquidSyntaxError("No file to include", self.context)
        parts = safe_split(self.attrs, " ", limit=1)
        if not check_quotes(parts[0]): # pragma: no cover
            # safe_split makes it impossible to Fail
            raise LiquidSyntaxError("Incorrectly quoted inclusion file: "
                                    f"{parts[0]!r}", self.context)
        parts[0] = unquote(parts[0])
        # also scan the directory with current template file
        incdirs = (self.config.include +
                   [Path(self.context.filename).resolve().parent])
        self.incfile = scan_file(parts[0], incdirs)
        incdirstr = ""
        if LOGGER.level < LIQUID_LOGLEVELID_DETAIL:
            incdirstr = "\nInclusion directories:\n"
            incdirstr += "\n".join(f"- {incdir}"
                                   for incdir in incdirs)
        if not self.incfile:
            raise LiquidSyntaxError("Cannot find file for inclusion: "
                                    f"{parts[0]}{incdirstr}", self.context)
        if not self.incfile.is_file():
            raise LiquidSyntaxError("File not exists for inclusion: "
                                    f"{parts[0]}{incdirstr}", self.context)
        if len(parts) > 1:
            vars_witheq = safe_split(parts[1], ',')
            for vareq in vars_witheq:
                if not vareq:
                    raise LiquidSyntaxError("Empty variable item in "
                                            f"{self.name!r} node", self.context)
            parts_eq = safe_split(vareq, '=', limit=1)
            if len(parts_eq) > 1:
                self.vars[parts_eq[0]] = self.try_mixed(parts_eq[1])
            elif parts_eq[0].isidentifier():
                self.vars[parts_eq[0]] = parts_eq[0]
            else:
                raise LiquidSyntaxError("A variable or a kwarg needed "
                                        "for variables passed to "
                                        f"{self.name!r} node", self.context)
        self.vars[LIQUID_RENDERED_APPEND] = LIQUID_RENDERED_APPEND
        self.vars[LIQUID_RENDERED_EXTEND] = LIQUID_RENDERED_EXTEND

    def parse_node(self):
        super().parse_node()
        funcname = f"{NodeInclude.LIQUID_INCLUDE_SOURCE}_{id(self)}"
        varnames = ", ".join(self.vars)
        kwargs = ", ".join(f"{key}={val}" for key, val in self.vars.items())
        inccode = LiquidCode()
        self.code.add_line('')
        self.code.add_line(f"def {funcname}({varnames}):")
        self.code.indent()
        self.code.add_line("'''Build source from included file'''")
        self.code.add_line('')
        self.code.add_code(inccode)
        self.code.add_line('')
        self.code.dedent()
        self.code.add_line(f"{funcname}({kwargs})")
        with self.config.tear() as teared_config:
            parser = self.context.parser.__class__(
                stream=None, code=inccode,
                shared_code=self.shared_code, filename=self.incfile,
                prev=(self.context.lineno, self.context.parser),
                config=teared_config)
            parser.parse()

@attr.s(kw_only=True)
class NodeBlock(Node):
    """@API
    Node {% block ... %} {% endblock %}"""
    def start(self):
        if not self.attrs:
            raise LiquidSyntaxError("A block name is required", self.context)
        if not self.attrs.isidentifier():
            raise LiquidSyntaxError(f"Not a valid block name: {self.attrs!r}",
                                    self.context)
    def parse_node(self):
        """Replace the parser's code with mine,
        so that the node inside me can be added to my code"""
        super().parse_node()
        # start a new code, this may be replaced by child template blocks
        blockcode = LiquidCode()
        # add it to parent, indentation automatically added
        self.context.parser.code.add_code(blockcode)
        # save to parent code object and index of this code object
        # to later replacement
        self.context.data.setdefault("blocks", {})
        # parent, index
        # we have to save parent code, as it could be parser's code
        # or parent block's code
        self.context.data.blocks[self.attrs] = (
            self.context.parser.code,
            len(self.context.parser.code.codes) - 1
        )
        self.context.parser.code = blockcode

    def end(self, name):
        super().end(name)
        # get parser's original code back
        self.context.parser.code = self.code

@attr.s(kw_only=True)
class NodeExtends(NodeVoid):
    """@API
    Node {% extends ... %}"""
    # make sure extends parsed before blocks
    # because we have to choose the right blocks
    defer = attr.ib(default=999, init=False, eq=False)
    extfile = attr.ib(default=None, init=False)
    lineno = attr.ib(default=0, init=False)
    def start(self):
        self.lineno = self.context.lineno
        if not self.attrs:
            raise LiquidSyntaxError("No file to extend", self.context)
        if not check_quotes(self.attrs):# pragma: no cover
            # safe_split makes it impossible to Fail
            raise LiquidSyntaxError("Incorrectly quoted extension file: "
                                    f"{self.attrs!r}", self.context)
        self.attrs = unquote(self.attrs)
        if any(isinstance(node, NodeExtends) for node in self.context.history):
            raise LiquidSyntaxError(f"Only one {self.name!r} node allowed"
                                    " in a template", self.context)
        # also scan the directory with current template
        extends_dirs = (self.config.extends +
                        [Path(self.context.filename).resolve().parent])
        self.extfile = scan_file(self.attrs, extends_dirs)
        extdirstr = ""
        if LOGGER.level < LIQUID_LOGLEVELID_DETAIL:
            extdirstr = "\nExtension directories:\n"
            extdirstr += "\n".join(f"- {extdir}" for extdir in extends_dirs)

        if not self.extfile:
            raise LiquidSyntaxError("Cannot find file for extension: "
                                    f"{self.attrs}{extdirstr}", self.context)
        if not self.extfile.is_file():
            raise LiquidSyntaxError("File not exists for extension: "
                                    f"{self.attrs}{extdirstr}", self.context)
    def parse_content(self):
        """Parse the mother template and impose my blocks into it
        And then replace the code of my parser with its."""
        # revert the lineno, as this is deferred
        self.context.lineno = self.lineno
        NodeIntact.parse_content(self)
        with self.config.tear() as teared_config:
            parser = self.context.parser.__class__(
                stream=None,
                shared_code=self.shared_code,
                code=LiquidCode(indent=self.code.ndent),
                config=teared_config,
                filename=self.extfile,
                prev=(self.context.lineno, self.context.parser)
            )
            parser.parse()
        # we need to replace the core stuff of current parser with
        # those of parser, so that the assembler will assemble the code
        # from parser
        curr_parser = self.context.parser
        # replace the blocks
        mother_blocks = parser.context.data.get("blocks", {})
        for bname, binfo in self.context.data.get("blocks", {}).items():
            if bname in mother_blocks:
                LOGGER.debug("[PARSER%2s] - Imposing block %r to [PARSER%2s] ",
                             self.context.nstack, bname, parser.context.nstack)
                mother_code, index = mother_blocks[bname]
                mother_code.codes[index] = binfo[0].codes[binfo[1]]
        # replace the code
        # what should we do with the shared code?
        curr_parser.code = parser.code

class NodeMode(NodeVoid):
    """Deprecated {% mode ... %}"""
    def start(self):
        warnings.warn("'mode' node is deprecated, use 'config' node instead",
                      DeprecationWarning)
    def parse_node(self):
        super().parse_node()
        self.config.mode = self.attrs

# regiester builtin nodes
register_node("assign", NodeAssign)
register_node("block", NodeBlock)
register_node("break", NodeBreak)
register_node("capture", NodeCapture)
register_node("case", NodeCase)
register_node("comment", NodeComment)
register_node("config", NodeConfig)
register_node("continue", NodeContinue)
register_node("cycle", NodeCycle)
register_node("decrement", NodeDecrement)
register_node("else", NodeElse)
register_node("else:", NodeElse)
register_node("elseif", NodeElseif)
register_node("elsif", NodeElseif)
register_node("elif", NodeElseif)
register_node("extends", NodeExtends)
register_node("extend", NodeExtends)
register_node("for", NodeFor)
register_node("from", NodeFrom)
register_node("if", NodeIf)
register_node("import", NodeImport)
register_node("include", NodeInclude)
register_node("increment", NodeIncrement)
register_node("mode", NodeMode)
register_node("python", NodePython)
register_node("raw", NodeRaw)
register_node("unless", NodeUnless)
register_node("when", NodeWhen)
register_node("while", NodeWhile)
