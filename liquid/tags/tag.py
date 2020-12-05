"""Basics for all tags"""
import re
from pathlib import Path

from lark import LarkError
from .grammar import Grammar
from .transformer import TagTransformer
from ..config import LIQUID_LOG_INDENT
from ..utils import shorten, logger, RequiredTags, get_tag_parser
from ..exceptions import LiquidSyntaxError, LiquidRenderError


class Tag: # pylint: disable=too-many-instance-attributes
    """The base class for all tags.

    Subclass should provide `start`, `grammar`, `transformer`, `base_grammar`
    via `__init_subclass__` to initialize a PARSER for the tag.

    If start is None, meaning no parser needed for this tag.

    Attributes:
        VOID: whether the tag is void, meaning True if there is
            no children allow otherwise False
        ELDER_TAGS: Prior tags pattern, used to valiate if this tag is
            in the right position.
            This should be a pyparsing object able to match the prior tags
            This is a list since a tag can be with multiple tags,
            For example, "else" with "if", "for" and "case"
        PARENT_TAGS: Parent tags where this tags allows to be put in
        YONGER_TAGS: A flag to tell whether a yonger sibling tag is allowed to
            be followed.
        SECURE: Is this tag secure?
            An insecure tag is not allowed in strict mode
        RAW: Whether all content should be treated as raw
        PARSER: Parser to parse the content
        BASE_GRAMMAR: The base grammar

        parsing_self: Whether this tag needs further parsing, or just hold it
        parsing_children: Whether we should parse then children,
            or just hold it
        name: The name that this tag hits (since a tag can have aliases)
        content: The content of the tag
        context: The context of the tag
        open_compact: Whether it is compact tag for open tag
        close_compact: Whether it is compact tag for close tag
        parser: The parser of the tag
        children: The children of the tag
        parent: The parent of the tag
        prev: The previous tag of this tag
        next: The next tag of this tag

    Args:
        hitname: The name that this tag hits (since a tag can have aliases)
        content: The content of the tag
        context: The context of the tag
        open_compact: Whether it is compact tag for open tag
        close_compact: Whether it is compact tag for close tag
        parser: The parser of the tag
    """
    __slots__ = ('name', 'content', 'context', 'open_compact', 'close_compact',
                 'parser', 'children', 'parent', 'parsed', 'prev', 'next',
                 'parsing_self', 'parsing_children')

    VOID = False
    ELDER_TAGS = ()
    PARENT_TAGS = ()
    YONGER_TAGS = True
    SECURE = True
    RAW = False

    START = None
    GRAMMAR = None
    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = Grammar(Path(__file__).parent / 'grammar.lark')


    PARSING_SELF = True
    PARSING_CHILDREN = True

    def __init__(self, # pylint: disable=too-many-arguments
                 hitname,
                 content,
                 context,
                 open_compact,
                 close_compact,
                 parser):
        # type: (str, str, Diot, bool, bool, "Parser") -> None
        self.name = hitname
        self.content = content
        self.context = context
        self.open_compact = open_compact
        self.close_compact = close_compact
        self.parser = parser
        self.children = []
        # Parent, previous and next tag object
        self.parent = self.prev = self.next = None
        self.parsed = None
        self.parsing_self = self.__class__.PARSING_SELF
        self.parsing_children = self.__class__.PARSING_CHILDREN

    def __init_subclass__(cls, use_parser=False):
        # type: (bool) -> None
        """Initialize a parser for subclass
        If use_parser is False, always try to generate a new parser for the
        subclass, otherwise, use the parent class's parser
        """
        if use_parser:
            # let it inherit
            return

        if not cls.START:
            cls.PARSER = None
        else:
            cls.PARSER = get_tag_parser(cls.START,
                                        cls.GRAMMAR,
                                        cls.TRANSFORMER,
                                        cls.BASE_GRAMMAR)

    # pylint: disable=inconsistent-return-statements
    def parse(self, force=False):
        # type: (bool) -> Optional[bool]
        """Parse the content of the tag"""

        if self.parsed is not None:
            return
        if not self.PARSER or (not force and not self.parsing_self):
            return

        try:
            self.parsed = self.PARSER.parse(self.content)
            return True
        except LarkError as lkerr:
            try:
                self.context.lineno += lkerr.line - 1
                self.context.colno += lkerr.column - 1
            except AttributeError: # pragma: no cover
                pass

            lkerr = re.sub(r' at line \d+, column \d+\.', '', str(lkerr))

            raise LiquidSyntaxError(
                f'Syntax error ({self.context.name}: '
                f'line {self.context.lineno + 1}, '
                f'column {self.context.colno + 1}): {lkerr}',
                self.context, self.parser
            ) from None

    def parse_children(self, base_level):
        """Parse the children if they are hold previouly"""
        for child in self.children:
            child.context.level = base_level + 1
            child.parse(force=True)
            child.parse_children(base_level + 1)

    def __repr__(self):
        # type: () -> str
        """The representation of the tag"""

        return (f"<{self.__class__.__name__}"
                f"({shorten(self.content, 30, placeholder=' [...]')!r}, "
                f"line {self.context.lineno + 1}, "
                f"column {self.context.colno + 1})>")

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        # pylint: disable=unused-argument
        """A function for sub-classes to implement
        We don't have to handle local/global envs, as it is handled
        by `render`. Here we only need to take care of the rendering
        """
        return self.content # pragma: no cover

    @property
    def parent_required(self):
        # type: () -> bool
        """Whether this tag is requiring a parent tag"""
        return isinstance(self.PARENT_TAGS, RequiredTags)

    @property
    def elder_required(self):
        # type: () -> bool
        """Whether this tag is requiring an elder tag"""
        return isinstance(self.ELDER_TAGS, RequiredTags)

    @property
    def eldest(self):
        # type: () -> Optional[Tag]
        """Find eldest tag"""
        elder = self.prev
        if not elder:
            return None
        while elder:
            if not elder.prev:
                return elder
            elder = elder.prev
        return None # pragma: no cover

    @property
    def closest_parent(self):
        # type: () -> Optional[Tag]
        """Find the closest parent"""
        parent = self.parent
        while parent:
            if parent.name in self.PARENT_TAGS:
                return parent
            parent = parent.parent
        return None # pragma: no cover

    def is_elder(self, tag):
        # type: (Tag) -> bool
        """Check if tag can be an elder of this tag"""
        return self.ELDER_TAGS and tag.name in self.ELDER_TAGS

    def is_parent(self, tag):
        # type: (Tag) -> bool
        """Check if tag can be a parent of this tag"""
        # If I don't require a parent, any un-VOID tag can be my parent
        if not self.parent_required:
            return True # pragma: no cover
        return tag.name in self.PARENT_TAGS

    def check_parents(self):
        # type: () -> bool
        """Check if we have valid direct or indirect parents

        This is done after parent and prev have been assigned

        For example, `continue` can be in `if`. We need to check if it
        parent `for` some where like this:
        ```liquid
        {% for ... %}
            {% if ... %}
                {% continue %}
            {% endif %}
        {% endfor %}
        ```
        """
        # I don't require any parents
        # or I optionally require some
        # pylint: disable=unsupported-membership-test
        if not self.parent_required:
            return True

        # Checking for direct parents? TODO?
        if not self.parent:
            return False # pragma: no cover

        parent = self.parent
        while parent:
            if self.is_parent(parent):
                return True
            parent = parent.parent
        return False

    def check_elders(self):
        # type: () -> bool
        """Check if required elders are placed"""
        if not self.elder_required:
            return True
        return self.prev and self.is_elder(self.prev)

    def _render_children(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        """Render the children

        This will be done recursively to render the whole template
        """
        rendered = ''
        for child in self.children:
            # local vars updated
            child_rendered, local_vars = child.render(local_vars, global_vars)
            rendered += child_rendered
        return rendered

    def _render_next(self, local_vars, global_vars, from_elder):
        """Render my next sibling"""
        if not self.next:
            return ''
        return self.next.render(local_vars, global_vars, from_elder)[0]

    def render(self, local_vars, global_vars, from_elder=False):
        # type: (dict, dict, bool) -> Tuple[str, dict]
        """Render the tag

        Args:
            local_vars: The local variables
            global_vars: The global variables
            from_elder: Whether the render is called from the elder tag
                If I have elder sibling tag, I can't run independently
                I am controlled by it

        Returns:
            The rendered string and local variables (maybe modified)
        """
        if self.prev and not from_elder:
            return '', local_vars
        logger.debug('%s  Rendering %r',
                     (self.context.level) * LIQUID_LOG_INDENT,
                     self)
        try:
            rendered = self._render(local_vars, global_vars)
        except Exception as exc:
            if hasattr(exc, 'lineno'):
                colno = getattr(exc, 'colno', 1)
                if exc.lineno > 1:
                    self.context.lineno += exc.lineno - 1
                    self.context.colno = colno - 1
                else:
                    self.context.colno += colno - 1

            raise LiquidRenderError(
                f'KeyError: {exc}' if isinstance(exc, KeyError) else str(exc),
                self.context,
                self.parser
            ).with_traceback(exc.__traceback__) from None
        else:
            return str(rendered), local_vars
