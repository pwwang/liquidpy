"""Tag else"""
from lark import v_args
from .transformer import TagTransformer
from .inherited import tag_manager
from .tag_if import TagIf
from ...utils import NOTHING, OptionalTags, RequiredTags
from ...exceptions import LiquidSyntaxError

@v_args(inline=True)
class TagElseTransformer(TagTransformer):
    """The transformer for tag else"""
    # pylint: disable=no-self-use
    def tag_else(self, test=NOTHING):
        """Get whatever passed by"""
        return test

@tag_manager.register
class TagElse(TagIf):
    """Tag else in python mode

    Allowed to be used with for, while and unless, too
    "else if" is also allowed here.
    """
    PARENT_TAGS = OptionalTags('case')
    # check this is invalid:
    # {% if ... %} {% else %} {% else if ... %} {% endif %}
    ELDER_TAGS = RequiredTags('if', 'unless', 'when', 'for',
                              'elsif', 'elif', 'else', 'while')

    START = 'tag_else'
    GRAMMAR = 'tag_else: ("if" test)?'
    TRANSFORMER = TagElseTransformer()

    def parse(self, force=False):
        # type: (bool) -> None
        """Check to see if there is any siblings after a bare {% else %} tag
        """
        if not super().parse(force):
            return

        # if this is {% else %}, we should not have any following siblings
        # This is a special case
        # Should we use another flag to tell the parse and raise the
        # exception earlier?
        if (self.prev and
                isinstance(self.prev, TagElse) and
                self.prev.parsed is NOTHING):
            raise LiquidSyntaxError(
                f'No tags allowed after {self!r}', self.context, self.parser
            )


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        if self.parsed is NOTHING:
            return self._render_children(local_vars, global_vars)

        return super()._render(local_vars, global_vars)
