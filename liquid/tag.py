"""Tag class for liquidpy"""
from .tagmgr import register_tag
from .tagfrag import try_render
from . import tags # pylint: disable=unused-import
from .exceptions import LiquidRenderError, LiquidException

class _PositionalTuple(tuple):
    def __new__(cls, *args):
        return super().__new__(cls, args)

class OptionalTags(_PositionalTuple):
    """Indicates the arguments are optional"""

class RequiredTags(_PositionalTuple):
    """Indicates the arguments are required"""

class Tag:

    """Tag class, for the Tags defined in the template
    such as `{% ... %}`, `{% ... %}`, as well as the literals

    Properties:
        name (str): The name of the tag
        data (lark.Tree): The parsed tag data
        context (TagContext): The context of this tag in the template
        parsed (TagParsed): Parsed object from the tag data
        children (list): List of children of the tag
        parent (Tag): The parent tag
        prev (Tag): The previous tag
        next (Tag): The next tag
        level (int): The level of the tag from the root
    """

    # whether the tag is void, meaning True if there is no children allow
    # otherwise False
    VOID = False
    # The syntax of this tag
    SYNTAX = None
    # Prior tags pattern, used to valiate if this tag is in the right
    # position.
    # This should be a pyparsing object able to match the prior tags
    # This is a list since a tag can be with multiple tags,
    # For example, "else" with "if", "for" and "case"
    ELDER_TAGS = None
    # Parent tags where this tags allows to be put in
    PARENT_TAGS = None
    # Whether this tag needs further parsing
    PARSING = True
    # Whether this tag is allowed in strict mode
    SECURE = True

    def __init__(self, name, data=None, context=None):
        self.name = name
        self.data = data
        self.context = context
        # The children of this tag
        self.children = []
        # Parent, previous and next tag object
        self.parent = self.prev = self.next = None
        self.level = 0

    def _require_parents(self):
        return isinstance(self.PARENT_TAGS, RequiredTags)

    def _require_elders(self):
        return isinstance(self.ELDER_TAGS, RequiredTags)

    def _can_be_parent(self, parent):
        if not self._require_parents():
            return True
        parent_name = parent.name if isinstance(parent, Tag) else parent
        return str(parent_name) in self.PARENT_TAGS

    def _can_be_elder(self, elder):
        elder_name = elder.name if isinstance(elder, Tag) else elder
        return self.ELDER_TAGS and str(elder_name) in self.ELDER_TAGS

    def _children_rendered(self, local_envs, global_envs):
        """Render the children
        This will be done recursively to render the whole template
        """
        rendered = ''
        for child in self.children:
            child_rendered, local_envs = child.render(local_envs, global_envs)
            rendered += child_rendered
        return rendered

    def _parents_valid(self):
        """Check if we have valid direct or indirect parents

        This is done after parent and prev have been assigned
        """
        # I don't require any parents
        # or I optionally require some
        # pylint: disable=unsupported-membership-test
        if not self._require_parents():
            return True

        # Checking for direct parents? TODO?
        if not self.parent:
            return False

        parent = self.parent
        while parent:
            if self._can_be_parent(parent):
                return True
            parent = parent.parent
        return False

    def _format_error(self, error=''):
        if isinstance(error, Exception):
            error = f"[{error.__class__.__name__}] {error}\n"
        elif callable(error):
            error = f"[{error.__name__}] {error}\n"
        elif error:
            error = f"{error}\n"
        else:
            error = ''

        formatted = [
            error,
            f'{self.context.parser.template_name}:'
            f'{self.context.line}:{self.context.column}',
            '-' * 80
        ]
        context_lines = self.context.parser.get_context(
            lineno=self.context.line
        )

        lineno_width = len(str(max(context_lines)))
        for lineno, line in context_lines.items():
            indicator = ('>' if self.context.line == lineno
                         else ' ')
            formatted.append(f'{indicator} {str(lineno).ljust(lineno_width)}'
                             f'. {line}')

        return '\n'.join(formatted) + '\n'

    def _cloest_parent(self, prtname):
        parent = self.parent
        while parent:
            if parent.name == prtname:
                return parent
            parent = parent.parent
        return None

    def _eldest(self):
        """Find eldest tag"""
        elder = self.prev
        if not elder:
            return None
        while elder:
            if not elder.prev:
                return elder
            elder = elder.prev
        return None # pragma: no cover

    def __repr__(self):
        context = f"line={self.context.line}, col={self.context.column}, "
        return (f'<Tag(name={self.name}, '
                f'{context if self.context else ""}'
                f'VOID={self.VOID})>')

    def _render(self, local_envs, global_envs):
        """Render the tag"""
        # pragma: no cover
        raise NotImplementedError()

    def _post_starting(self):
        """Hook for actions after tag relationships have been resolved."""

    def render(self, local_envs, global_envs, from_elder=False):
        """Render the tag, using the envs

        Args:
            local_envs (dict): The local environments
            global_envs (dict): The global environments
            from_elder (bool): Whether the rendering is called from
                an elder tag. If I have a previous tag, then I must be
                rendered from the previous tag.

        Returns:
            tuple: The rendered object and the local environment that may
                be changed by this tag.
        """
        if self.prev and not from_elder:
            return '', local_envs
        try:
            return self._render(local_envs, global_envs), local_envs
        except LiquidException as lre:
            raise lre
        except Exception as exc:
            raise LiquidRenderError(self._format_error(exc))

@register_tag('LITERAL')
class TagLiteral(Tag):
    """Literal tag"""
    VOID = True
    LEFT_COMPACT = RIGHT_COMPACT = False

    def _render(self, local_envs, global_envs):
        data = str(self.data)
        if self.LEFT_COMPACT:
            data = data.lstrip()
        if self.RIGHT_COMPACT:
            data = data.rstrip()
        return data

@register_tag('RAW')
class TagRaw(Tag):
    """Raw tag"""
    VOID = True

    def _render(self, local_envs, global_envs):
        return str(self.data)

@register_tag('OUTPUT')
class TagOutput(Tag):
    """Output/varable tag"""
    VOID = True
    def _render(self, local_envs, global_envs):
        rendered = try_render(self.data, local_envs, global_envs)
        return str(rendered) if rendered is not None else ''

@register_tag('ROOT')
class TagRoot(Tag):
    """The virtual root tag"""
    def _render(self, local_envs, global_envs):
        return self._children_rendered(local_envs, global_envs)
