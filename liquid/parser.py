"""
The parser for liquidpy
"""
import logging
from diot import Diot
from .stream import LiquidStream
from .exceptions import LiquidSyntaxError
from .nodes import (
    NodeLiquidLiteral,
    NodeLiquidComment,
    NodeIntact,
)
from .expression import NodeLiquidExpression
from .code import LiquidCode
from .defaults import (
    LIQUID_COMPACT_TAGS,
    LIQUID_PAIRED_TAGS,
    LIQUID_OPEN_TAGS,
    LIQUID_LOGGER_NAME,
    LIQUID_EXPR_OPENTAG,
    LIQUID_EXPR_OPENTAG_COMPACT,
    LIQUID_COMMENT_OPENTAG,
    LIQUID_COMMENT_OPENTAG_COMPACT,
    LIQUID_STATE_OPENTAG,
    LIQUID_STATE_OPENTAG_COMPACT,
    LIQUID_MAX_STACKS,
    LIQUID_DEBUG_SOURCE_CONTEXT,
    LIQUID_NODES,
    LIQUID_RENDERED,
    LIQUID_CONTEXT,
    LIQUID_RENDER_FUNC_PREFIX,
    LIQUID_RENDERED_APPEND,
    LIQUID_RENDERED_EXTEND
)

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def _multi_line_support(string):
    """
    Support multi-line statements, comments (tag) and expressions
    Turn this:
    ```
    assign a = xyz | filter1
                    | filter2
    ```
    to:
    ```
    assign a = xyz | filter1 | filter2
    ```
    """
    lines = string.splitlines()
    lens = len(lines)
    lines = (line.rstrip() if i == 0
             else line.lstrip() if i == lens - 1
             else line.strip()
             for i, line in enumerate(lines))
    return ' '.join(lines)

class LiquidParser: # pylint: disable=too-many-instance-attributes
    """@API
    Parse a file or a string template"""
    def __init__(self, # pylint: disable=too-many-arguments
                 filename,
                 prev,
                 config,
                 stream=None,
                 shared_code=None,
                 code=None):
        """@API
        Constructor for LiquidParser
        @params:
            filename (str): The filename of the template
            prev (LiquidParse): The previous parser
            config (LiquidConfig): The configuration
            stream (stream): The stream to parse instead of the file of filename
            shared_code (LiquidCode): The shared code
            code (LiquidCode): The code object
        """
        self.stream = stream or LiquidStream.from_file(filename)
        self.shared_code = shared_code
        self.code = code or LiquidCode()
        # previous lineno and parser, to get call stacks
        self.prev = prev
        nstack = prev[1].context.nstack + 1 if prev else 1

        LOGGER.debug("[PARSER%2s] Initialized from %s", nstack, filename)
        # deferred nodes
        self.deferred = []
        self.config = config
        self.context = Diot(filename=filename,
                            lineno=1,
                            history=[],
                            # the data passed on during parsing
                            data=Diot(),
                            stacks=[],
                            # which parser stack I am at
                            nstack=nstack,
                            # attach myself to the context
                            parser=self)

        # previous closing tag
        # we need it to do compact for next literal
        self.endtag = None

        if nstack >= LIQUID_MAX_STACKS:
            raise LiquidSyntaxError(f'Max stacks ({nstack}) reached',
                                    self.context)

    def call_stacks(self, lineno=None):
        """@API
        Get call stacks for debugging
        @params:
            lineno (int): Current line number
        @returns:
            (list): The assembled call stacks
        """
        stacks = [(lineno or self.context.lineno, self)]
        prev = self.prev
        while prev:
            stacks.append(prev)
            prev = prev[1].prev

        ret = []
        for lnno, parser in reversed(stacks):
            ret.append(f"File {parser.context.filename}")
            ret.extend(f"  {line}"
                       for line in parser.stream.get_context(
                           lnno,
                           LIQUID_DEBUG_SOURCE_CONTEXT if parser is self else 0
                       ))
        return ret

    def parse(self):
        """@API
        Start parsing the template"""
        # Let's scan for the next open tag {%, {{, {#
        # Even it's quoted or wrapped by brackets
        string, tag = self.stream.until(LIQUID_OPEN_TAGS, wraps=[], quotes=[])

        # pass the tag as well, to know if it is compact
        self.parse_literal(string, tag)

        if tag in (LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT):
            # closing tag will be found in it
            self.parse_expression(tag)
            # keep parsing
            self.parse()

        elif tag in (LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT):
            self.parse_comment(tag)
            self.parse()

        elif tag in (LIQUID_STATE_OPENTAG, LIQUID_STATE_OPENTAG_COMPACT):
            self.parse_statement(tag)
            self.parse()

        else: # no more tags
            if self.context.stacks:
                raise LiquidSyntaxError(
                    f"Node {self.context.stacks[-1].name!r} not closed",
                    self.context
                )
            for defer in sorted(self.deferred,
                                key=lambda x: x.defer,
                                reverse=True):
                defer.parse_content()

        return self.code

    def _expect_closing_tag(self, tag):
        """
        Get the closing tag of an open one
        @params:
            tag (str): The open tag
        @returns:
            (str): The content of the node.
            For example: `abc` of `{% abc %}`. `%}`
            will be saved in `self.endtag`
        """
        paired_tags = None
        for opentags, endtags in LIQUID_PAIRED_TAGS:
            if tag in opentags:
                paired_tags = endtags
                break

        nodestr, closetag = self.stream.until(paired_tags)

        # if we have any open tags in nodestr, for example
        # tag nodestr    closetag
        # |  |           |
        # {% ... {%- raw %}
        # we should raise an exception, as first tag is not closed
        _, opentag = LiquidStream.from_string(nodestr).until(LIQUID_OPEN_TAGS)
        if opentag:
            raise LiquidSyntaxError(f"Unclosed tag {tag!r}", self.context)

        self.context.lineno += nodestr.count("\n")
        if not closetag:
            raise LiquidSyntaxError("Expecting a closing tag "
                                    f"for {tag!r}", self.context)
        nodestr = nodestr.strip()
        if not nodestr:
            raise LiquidSyntaxError("Empty node", self.context)
        self.endtag = closetag
        return nodestr

    def _expect_end_node(self, name):
        """
        Get possible ending tags, like '{% endraw %}', '{%-endraw-%}'
        Only one space allowed
        """
        content = ''
        compact_right = self.config.mode == "compact"
        while True:
            string, tag = self.stream.until(LIQUID_OPEN_TAGS,
                                            wraps=[], quotes=[])
            if not tag:
                raise LiquidSyntaxError(f"Expecting an end node for {name!r}",
                                        self.context)

            self.context.lineno += string.count('\n')
            cursor = self.stream.cursor

            content += string
            compact_right = (tag in LIQUID_COMPACT_TAGS or
                             self.config.mode == "compact")

            paired_tags = [ptags[1] for ptags in LIQUID_PAIRED_TAGS
                           if tag in ptags[0]][0]
            nodestr, closetag = self.stream.until(paired_tags)

            # {%
            # {% endblock %}
            # tag could match the first {%
            # then nodestr will be "\n{% endblock"
            # and close tag "%}"
            # The problem is that {% endblock %} will be ignored
            # We need to go back to cursor there is an open tag in nodestr
            # and of course nodestr is not gonna match end{name}
            if any(opentag in nodestr for opentag in LIQUID_OPEN_TAGS):
                content += tag
                self.stream.stream.seek(cursor)
                continue

            self.context.lineno += nodestr.count('\n')
            if closetag and nodestr.strip() == f"end{name}":
                self.endtag = closetag
                return content, compact_right

            content += tag + nodestr + closetag
        # we shall not reach here
        # if no open tag hit, LiquidSyntaxError raised
        # otherwise nodestr checked, if name hit, returns, else
        # go find the open tag until no open tags found
        # return content, compact_right


    def parse_literal(self, string, tag):
        """@API
        Parse the literal texts
        @params:
            string (str): The literal text
            tag (str): The end tag
        """
        if not string:
            return

        lineno_inc = string.count('\n')

        if self.endtag in LIQUID_COMPACT_TAGS or self.config.mode == "compact":
            string = string.lstrip(" \t").lstrip('\n')

        if tag in LIQUID_COMPACT_TAGS or self.config.mode == "compact":
            string = string.rstrip(" \t").rstrip('\n')

        if string:
            NodeLiquidLiteral(attrs=string,
                              code=self.code,
                              shared_code=self.shared_code,
                              context=self.context).parse_node()
        self.endtag = None
        self.context.lineno += lineno_inc

    def parse_expression(self, tag):
        """@API
        Parse the expressions like `{{ 1 }}`
        @params:
            tag (str): The open tag
        """
        nodestr = self._expect_closing_tag(tag)
        nodestr = _multi_line_support(nodestr)
        NodeLiquidExpression(attrs=nodestr,
                             code=self.code,
                             shared_code=self.shared_code,
                             config=self.config,
                             context=self.context).parse_node()

    def parse_comment(self, tag):
        """@API
        Parse the comment tag `{##}` or `{#--#}`
        @params:
            tag (str): The open tag.
        """
        nodestr = self._expect_closing_tag(tag)
        nodestr = _multi_line_support(nodestr)
        comment_node = NodeLiquidComment(context=self.context)
        comment_node.start()
        comment_node.parse_node()

    def parse_statement(self, tag):
        """@API
        Parse the statement node `{% ... %}`
        @params:
            tag (str): The open tag
        """
        nodestr = self._expect_closing_tag(tag)
        nodestr = _multi_line_support(nodestr)

        try:
            name, attrs = nodestr.split(maxsplit=1)
        except ValueError:
            name, attrs = nodestr, ''

        if name[:3] == "end":
            if attrs:
                raise LiquidSyntaxError("End node should take no expressions",
                                        self.context)
            if not self.context.stacks:
                raise LiquidSyntaxError(f"Got closing node {name!r}, "
                                        "but no node opened", self.context)
            self.context.stacks[-1].end(name[3:])
            return

        if name not in LIQUID_NODES:
            raise LiquidSyntaxError(f"Unknown node {name!r}", self.context)

        node = LIQUID_NODES[name](name=name,
                                  attrs=attrs,
                                  code=self.code,
                                  shared_code=self.shared_code,
                                  config=self.config,
                                  context=self.context)
        node.start()
        node = node.parse_node() or node
        # fetch the content between {% raw ... %} {% endraw %}
        if isinstance(node, NodeIntact):
            compact_left = (self.endtag in LIQUID_COMPACT_TAGS or
                            self.config.mode == "compact")
            content, compact_right = self._expect_end_node(name)
            node.content = content
            node.compact_left = compact_left
            node.compact_right = compact_right
            # we anyway hit the end node
            node.end(name)

        if hasattr(node, "defer"):
            LOGGER.debug("[PARSER%2s] - Deferring node %r at priority %s",
                         self.context.nstack, node.name, node.defer)
            self.deferred.append(node)

        elif isinstance(node, NodeIntact):
            node.parse_content()

    def assemble(self, context):
        """@API
        Assemble it to executable codes, only when final is True
        This may be re-assembled with different context
        So we should not do anything with self.code and self.shared_code
        @params:
            context (diot): The context to render the template
        """

        funcname = f"{LIQUID_RENDER_FUNC_PREFIX}_{id(self)}"
        finalcode = LiquidCode()
        finalcode.add_line(f"def {funcname}({LIQUID_CONTEXT}):")
        finalcode.indent()
        finalcode.add_line("'''Main entrance function to render the "
                           "template'''")
        finalcode.add_line('')
        finalcode.add_line("# Rendered content")
        finalcode.add_line(f"{LIQUID_RENDERED} = []")
        finalcode.add_line(f"{LIQUID_RENDERED_APPEND} = "
                           f"{LIQUID_RENDERED}.append")
        finalcode.add_line(f"{LIQUID_RENDERED_EXTEND} = "
                           f"{LIQUID_RENDERED}.extend")
        finalcode.add_line("")
        finalcode.add_line("# Environment and variables")
        for key in context:
            finalcode.add_line(f"{key} = {LIQUID_CONTEXT}[{key!r}]")
        finalcode.add_code(self.shared_code)
        finalcode.add_code(self.code)
        finalcode.add_line("")
        finalcode.add_line("return ''.join(str(x) for x in "
                           f"{LIQUID_RENDERED})")
        return finalcode, funcname
