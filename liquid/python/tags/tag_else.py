from lark import v_args
from .transformer import TagTransformer
from .inherited import tag_manager
from .tag_if import TagIf
from ...utils import NOTHING, OptionalTags, RequiredTags
from ...exceptions import LiquidSyntaxError

@v_args(inline=True)
class TagElseTransformer(TagTransformer):

    def tag_else(self, test=NOTHING):
        return test

@tag_manager.register
class TagElse(TagIf):

    PARENT_TAGS = OptionalTags('case')
    # check this is invalid:
    # {% if ... %} {% else %} {% else if ... %} {% endif %}
    ELDER_TAGS = RequiredTags('if', 'unless', 'when', 'for',
                              'elsif', 'elif', 'else', 'while')

    START = 'tag_else'
    GRAMMAR = 'tag_else: ("if" test)?'
    TRANSFORMER = TagElseTransformer()

    def parse(self, force=False):
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
                f'No tags allowed after {self!r}',
                self.context,
                self.parser
            )


    def _render(self, local_vars, global_vars):
        if self.parsed is NOTHING:
            return self._render_children(local_vars, global_vars)

        return super()._render(local_vars, global_vars)
