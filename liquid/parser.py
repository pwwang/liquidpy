"""The parser for liquidpy"""
from collections import deque
from diot import Diot
from .config import LIQUID_LOG_INDENT
from .nodes import NodeScanner
from .utils import logger
from .tags import tag_manager
from .exceptions import LiquidSyntaxError

class Visitor:
    # pylint: disable=too-few-public-methods
    """Vistor to visit parsed node

    Attributes:
        root: The root tag
        stack: The tag stack, used to resolve the structure
        blocks: The block tags, used to replace the mother's ones
        has_mother: Indicates whether this template is extended from
            a mother template

    Args:
        root: The root tag
    """
    __slots__ = ('root', 'stack', 'blocks', 'has_mother', '_prev_tag')

    def __init__(self, root):
        # type: (Tag) -> None
        self.root = root
        self.stack = deque()
        self.blocks = {}
        self.has_mother = False
        # use to hold the compact
        self._prev_tag = None

    def visit(self, tag):
        # type: (Tag) -> None
        """Visit the tag

        Args:
            tag: The tag
        """
        # whitespace control
        if tag.name == 'LITERAL':
            tag.open_compact = self._prev_tag and self._prev_tag.close_compact
        elif self._prev_tag and self._prev_tag.name == 'LITERAL':
            self._prev_tag.close_compact = tag.open_compact

        self._prev_tag = tag

        if tag.name.startswith('end'):
            self._end_tag(tag)
        else:
            self._start_tag(tag)

        tag.parse()

        if tag.name == 'block':
            self.blocks[tag.parsed] = tag

    def _start_tag(self, tag):
        # type: (Tag) -> None
        """Encounter a start tag, try to solve the structure"""
        if not self.stack:
            if tag.parent_required:
                raise LiquidSyntaxError(
                    f"One of the parent tags is required: {tag.PARENT_TAGS}",
                    tag.context,
                    tag.parser
                )
            if tag.elder_required:
                raise LiquidSyntaxError(
                    f"One of the elder tags is required: {tag.ELDER_TAGS}",
                    tag.context,
                    tag.parser
                )
            self.root.children.append(tag)
            tag.parent = self.root
        else:
            # assign siblings
            if tag.is_elder(self.stack[-1]):
                # let parent handle coming tags
                prev_tag = self.stack.pop()
                prev_tag.next = tag
                tag.prev = prev_tag

                tag.context.level = prev_tag.context.level

            # now self.stack[-1] should be the parent
            if self.stack:
                self.stack[-1].children.append(tag)
                tag.parent = self.stack[-1]
                tag.context.level = tag.parent.context.level + 1
                # If parent is holding parsing, I am holding too.
                tag.parsing_self = tag.parent.parsing_children
                tag.parsing_children = tag.parent.parsing_children

            # parent check
            # we need to check if a tag is under the right parent
            if not tag.check_parents():
                raise LiquidSyntaxError(
                    f"Tag {tag.name!r} expects parents: {tag.PARENT_TAGS}",
                    tag.context,
                    tag.parser
                )

            # elder check
            # if a node is requiring elders, it should not be the first child
            if not tag.check_elders():
                raise LiquidSyntaxError(
                    f"Tag {tag.name!r} expects elder tags: {tag.ELDER_TAGS}",
                    tag.context,
                    tag.parser
                )

        if not tag.VOID:
            self.stack.append(tag)

    def _end_tag(self, tag):
        # type: (Tag) -> None
        """Handle tag relationships when closing a tag."""
        tagname = tag.name[3:]
        if not self.stack:
            raise LiquidSyntaxError(
                f"Unexpected endtag: {tag!r}",
                tag.context,
                tag.parser
            )

        last_tag = self.stack[-1]
        last_eldest = last_tag.eldest or last_tag
        while last_tag:
            if last_eldest.name == tagname:
                self.stack.pop()
                break
            # If a tag needs parent, supposingly, the parent will close
            # for it
            # Otherwise, here, it needs to be closed
            if not last_eldest.parent_required:
                raise LiquidSyntaxError(
                    f"Tag unclosed: {last_eldest!r}",
                    last_eldest.context,
                    last_eldest.parser
                )
            self.stack.pop()
            last_tag = self.stack[-1] if self.stack else None
            last_eldest = (last_tag.eldest if last_eldest else None) or last_tag

class Parser:
    # pylint: disable=too-few-public-methods
    """The root parser for liquidpy

    This parses the stream into tags, and each tag will be handled by
    different parser using lark

    Attibutes:
        NODESCANNER_CLASS: The node scanner class
        VISITOR_CLASS: The visitor class

        config: The configuration
        context: The context
        parent: The parent parser
        nodescanner: The node scanner
        visitor: The visitor for tags

    Args:
        meta: The template meta data
        config: The configuration
        context: The context
        level: The level of the parser
    """
    __slots__ = ('config', 'context', 'parent', 'nodescanner', 'visitor')

    NODESCANNER_CLASS = NodeScanner # type: Type[NodeScanner]
    VISITOR_CLASS = Visitor # type: Type[Visitor]

    def __init__(self, meta, config, context=None, level=0):
        # type: (TemplateMeta, Dict, Optional[Diot], Optional[int]) -> None
        self.config = config
        self.context = context or Diot(
            name=meta.name,
            path=meta.path,
            stream=meta.stream,
            lineno=0,
            colno=0,
            level=level
        )
        self.parent = None
        self.nodescanner = self.NODESCANNER_CLASS(self.context, self)
        self.nodescanner.open_context = self.context.copy()
        self.visitor = self.VISITOR_CLASS(tag_manager.get('ROOT')(
            hitname='ROOT',
            content=f'{meta.name}::ROOT',
            context=self.nodescanner.open_context,
            open_compact=False,
            close_compact=False,
            parser=self
        ))

    def parse(self):
        # type: () -> Tag
        """Parser the template for later rendering.

        Returns:
            The root tag for later rendering
        """
        logger.debug('%s- PARSING %r ...',
                     self.context.level * LIQUID_LOG_INDENT,
                     self.context.name)
        while True:
            scanned = self.nodescanner.consume(
                self.context.stream
            ) # type: Optional[bool, Node]

            if scanned is False:
                self.visitor.root.parse()
                logger.debug('%s  END PARSING.',
                             self.context.level * LIQUID_LOG_INDENT)
                break
            if scanned is True:
                continue
            # Node
            tag = scanned.tag

            if not tag.SECURE and self.config.strict:
                raise LiquidSyntaxError(
                    f"Tag not allowed in strict mode: {tag!r}",
                    tag.context, self
                )
            self.visitor.visit(tag)

        return self.visitor.root
