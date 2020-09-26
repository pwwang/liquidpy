"""Definition of nodes and node scanner"""
from .config import LIQUID_LOG_INDENT
from .tags import tag_manager
from .utils import analyze_leading_spaces, logger
from .exceptions import LiquidSyntaxError

class Node:
    """A node of liquidpy

    Serves as a bridge between parser and tags for scanning
    Should be one of:
    - literal node: ...
    - output node: {{ ... }}
    - comment node: {# ... #}
    - tag node: {% ... %}

    Attributes:
        OPEN_TAG: The open tags for the node
        CLOSE_TAG: The close tags for the node
        TAG_MANAGER: The tag manager
        name: The name of the node

        open_compact: Whether open tag is compact
        close_compact: Whether close tag is compact
        content: The content of the node
        context: The context of the node

    Args:
        content: The content of the node
        context: The context of the node
        parser: The parser
        open_tag: The open tag of the node
        close_tag: The close tag of the node

    """

    OPEN_TAG = ()  # type: Tuple[str]
    CLOSE_TAG = () # type: Tuple[str]
    name = '' # type: str

    __slots__ = ('open_compact', 'close_compact', 'context', 'content', '_tag')

    def __init__(self, # pylint:disable=too-many-arguments
                 content,
                 context,
                 parser,
                 open_tag='',
                 close_tag=''):
        # type: (str, str, str, Optional[Diot], "Parser") -> None
        self.open_compact = '-' in open_tag
        self.close_compact = '-' in close_tag
        self.context = context
        self.content = content
        self._update_context(open_tag)
        tag = self._get_tag(parser)
        self._tag = tag

    def __init_subclass__(cls, tag_manager=tag_manager):
        # pylint: disable=redefined-outer-name
        cls.TAG_MANAGER = tag_manager

    @property
    def tag(self):
        # type: () -> "Tag"
        """Get the tag from the node"""
        return self._tag

    @property
    def raw(self):
        # type: () -> bool
        """Check whether this node is in raw mode"""
        return self.tag.RAW

    def _update_context(self, open_tag):
        """Update the context to the start of the content"""

    def _get_tag(self, parser):
        # type: ("Parser") -> "Tag"
        """Get the tag

        Args:
            parser: The parser

        Returns:
            The tag that can is associated with this node
        """
        tag_class = self.TAG_MANAGER.get(self.name)
        if not tag_class:
            try:
                self.context.lineno = self._tagname_line
                self.context.colno = self._tagname_column - 1
            except AttributeError: # pragma: no cover
                pass
            raise LiquidSyntaxError(f'No such tag: {self.name}',
                                    self.context,
                                    parser)
        name = self.name
        content = self.content
        if name.startswith('end'):
            content = name[3:]
        return tag_class(name,
                         content,
                         self.context,
                         self.open_compact,
                         self.close_compact,
                         parser)

class NodeLiteral(Node):
    """The literal node"""
    name = "LITERAL"

class NodeOutput(Node):
    """The output node"""
    OPEN_TAG = '{{', '{{-'
    CLOSE_TAG = '}}', '-}}'
    name = "OUTPUT"

    def _update_context(self, open_tag):
        self.context.colno += len(open_tag)
        nnewline, nspaces = analyze_leading_spaces(self.content)
        if nnewline > 0:
            self.context.lineno += nnewline
            self.context.colno = nspaces
        else:
            self.context.colno += nspaces

        self.content = self.content.strip()

class NodeTag(Node):
    """The opening of a tag node"""
    OPEN_TAG = '{%', '{%-'
    CLOSE_TAG = '%}', '-%}'

    def __init__(self, *args, **kwargs):
        self._tagname_line = self._tagname_column = 0
        super().__init__(*args, **kwargs)

    def _update_context(self, open_tag):
        NodeOutput._update_context(self, open_tag)
        self._tagname_line = self.context.lineno
        self._tagname_column = self.context.colno
        splits = self.content.strip().split(maxsplit=1) # type: List[str]
        self.name = splits[0]                           # type: str

        content = splits[1] if len(splits) > 1 else ''
        self.context.colno += len(self.name)
        n_newline, n_spaces = analyze_leading_spaces(
            self.content[len(self.name):]
        )
        if n_newline > 0:
            self.context.lineno += n_newline
            self.context.colno = n_spaces
        else:
            self.context.colno += n_spaces

        self.content = content

class NodeScanner:
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Scanning for the nodes

    Attributes:
        LITERAL: The literal node
        NODES: The possible nodes
        OPEN_CHARS: The start characters of open tags for those nodes
            This is to speed up the lookup for a potential hit of a node

        context: The context of the potential node
        open_context: Where the open tag hits
        hit: The node we hit
            This will be only fit when there is only one type of node hit
        literal_buffer: The buffer for literal nodes
            This will not consume the potential node
        opentag_buffer: The buffer for open tags
        closetag_buffer: The buffer for close tags
        content_buffer: The buffer for content of potential nodes
        escape: Whether the previous character is an escape (`\\`)
        rawtag: The matched raw tag name
        parser: The parser
    """

    __slots__ = ('context', 'open_context', 'hit', 'literal_buffer',
                 'opentag_buffer', 'content_buffer', 'closetag_buffer',
                 'escape', 'rawtag', 'parser')


    LITERAL = NodeLiteral          # type: NodeLiteral
    NODES = (NodeOutput, NodeTag)  # type: Tuple[Type[Node]]
    OPEN_CHARS = set(tag[0] for node in NODES
                     for tag in node.OPEN_TAG) # type: Set[str]

    def __init__(self, context, parser):
        # type: (Diot, "Parser") -> None

        self.context = context      # type: Diot
        self.open_context = None    # type: Diot
        self.hit = None             # type: Optional[Node]
        self.literal_buffer = ''    # type: str
        self.opentag_buffer = None  # type: str
        self.closetag_buffer = None # type: str
        self.content_buffer = None  # type: str
        self.escape = None          # type: bool
        self.rawtag = None          # type: Optional[str]
        self.parser = parser        # type: Parser
        self._clear_state()

    def _clear_state(self):
        """Clear the hit state."""
        self.hit = None
        self.opentag_buffer = ''
        self.closetag_buffer = ''
        self.content_buffer = ''

    def _summarize(self, end=False):
        """Summarize the residue"""

        # we don't have any node hit, summarize the literal
        if not self.hit:
            # context is mutable, have to copy it to keep current context
            literal = (self.literal_buffer + self.opentag_buffer
                       if end
                       else self.literal_buffer) # type: str
            self.literal_buffer = ''
            if literal:
                node = self.LITERAL(literal, self.open_context, self.parser)
                logger.debug('[dim italic]%s  Found %r[/dim italic]',
                             self.context.level * LIQUID_LOG_INDENT,
                             node.tag,
                             extra={"markup": True})
                return node
            return not end

        # We got a hit, if no closetag hit yet,
        # we need to summarize previous literals
        if not self.closetag_buffer:
            if self.literal_buffer:
                node = self.LITERAL(self.literal_buffer,
                                    self.open_context,
                                    self.parser)
                self.literal_buffer = ''
                logger.debug('[dim italic]%s  Found %r[/dim italic]',
                             self.context.level * LIQUID_LOG_INDENT,
                             node.tag,
                             extra={"markup": True})
                self.open_context = self.context.copy()
                self.open_context.colno -= len(self.opentag_buffer)
                return node
            if not end:
                return True
        if self.closetag_buffer in self.hit.CLOSE_TAG:
            # let's see if we are inside a raw tag
            if self.rawtag:
                # NodeTag
                if (not self.hit.name and
                        self.content_buffer.strip() == 'end' + self.rawtag):
                    self.rawtag = None
                else:
                    self.literal_buffer += (self.opentag_buffer +
                                            self.content_buffer +
                                            self.closetag_buffer)
                    logger.debug('[dim italic]%s  Gave up %r (inside raw tag)'
                                 '[/dim italic]',
                                 self.context.level * LIQUID_LOG_INDENT,
                                 self.hit.__name__,
                                 extra={"markup": True})
                    self._clear_state()
                    if not end:
                        return True

            node = self.hit(self.content_buffer,
                            self.open_context,
                            self.parser,
                            self.opentag_buffer,
                            self.closetag_buffer) # type: Type[Node]

            logger.debug('%s  Found %r',
                         self.context.level * LIQUID_LOG_INDENT,
                         node.tag)
            if node.raw:
                self.rawtag = node.name

            self._clear_state()
            return node

        context = self.open_context or self.context
        raise LiquidSyntaxError(
            f'Unclosed node {self.hit.__name__} ({context.name}, '
            f'line {context.lineno + 1}, '
            f'column {context.colno + 1})',
            context,
            self.parser
        )

    def _open_node(self, char):
        # type: (str) -> Optional[bool]
        """check if char is opening a node only when one definite
        type of node hit"""
        if ((not self.opentag_buffer and not char in self.OPEN_CHARS) or
                self.content_buffer):
            return False

        opentag = self.opentag_buffer + char # type: str
        # See if we already have a hit, see if we hit '-'
        if self.hit:
            return opentag in self.hit.OPEN_TAG

        potential_hits = [node for node in self.NODES
                          if any(tag.startswith(opentag)
                                 for tag in node.OPEN_TAG)]

        if len(potential_hits) == 1:
            self.hit = potential_hits[0]
            return True
        if len(potential_hits) > 1:
            return None
        return False

    def _close_node(self, char):
        # type: (str) -> Optional[bool]
        """Check if a char is closing a node"""

        closetag = self.closetag_buffer + char # type: str
        if closetag in self.hit.CLOSE_TAG:
            return True
        if any(ctag.startswith(closetag) for ctag in self.hit.CLOSE_TAG):
            return None
        return False

    def _add_to_buffer(self, char):
        # type: (str) -> Union[bool, Type[Node]]
        """Add character to buffer, and decide whether we should do a summary
        on the state"""
        # When should we do a summary:
        # 1. When a potential hit is determined (ie `{%` hit)
        # 2. When a hit closes (ie `%}` hit)
        # 3. Stream end hit
        if self.escape:
            char = f'\\{char}'
            self.escape = False

        if not self.hit:
            opened = self._open_node(char) # type: Optional[bool]
            if opened is True: # pragma: no cover
                self.opentag_buffer += char
                ret = self._summarize()
                logger.debug('[dim italic]%s  Opened potential node: %s '
                             '(line: %s, column: %s)[/dim italic]',
                             self.context.level * LIQUID_LOG_INDENT,
                             self.hit.__name__,
                             self.open_context.lineno + 1,
                             self.open_context.colno + 1,
                             extra={"markup": True})
                return ret

            if opened is False:
                self.literal_buffer += self.opentag_buffer + char
                self.opentag_buffer = ''

            else: # hit potentially, multiple node types hit
                self.opentag_buffer += char

        elif self._open_node(char) is False:
            closed = self._close_node(char)
            if closed is True:
                self.closetag_buffer += char
                node = self._summarize()
                if isinstance(node, bool):
                    return node
                self.open_context = self.context.copy()
                logger.debug('[dim italic]%s  Closed node: %s[/dim italic]',
                             self.context.level * LIQUID_LOG_INDENT,
                             f"{node.__class__.__name__}({node.tag.name})"
                             if isinstance(node, NodeTag)
                             else node.name,
                             extra={"markup": True})
                return node

            if closed is False:
                self.content_buffer += self.closetag_buffer + char
                self.closetag_buffer = ''

            else: # potentially closed
                self.closetag_buffer += char

        else: # we hit '-'
            self.opentag_buffer += char
        return True

    def consume(self, stream):
        # type: (IO) -> Union[bool, Type[Node]]
        """Consume the character of a stream

        if it is empty, then we hit the end of the stream.
        Otherwise, we need to update the context, and add the character to the
        buffer.

        Args:
            stream: The stream to consume

        Returns:
            True: we should continue consuming
            False: we should stop consuming (we hit the end of the stream)
            Node: A complete node hit
        """
        char = stream.read(1) # type: str
        if not char:
            return self._summarize(end=True)

        if char == '\n':
            self.context.lineno += 1
            self.context.colno = 0
            return self._add_to_buffer(char)
        if char == '\\':
            self.escape = not self.escape
            self.context.colno += 1
            if not self.escape:
                return self._add_to_buffer(char)
        else:
            self.context.colno += 1
            return self._add_to_buffer(char)

        return True
