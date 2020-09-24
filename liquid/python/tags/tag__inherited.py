"""Tags inherited from standard mode"""
from lark import v_args
from .inherited import tag_manager, Tag, BASE_GRAMMAR
from .transformer import TagTransformer
from ...utils import OptionalTags, RequiredTags
from ...tags.transformer import render_segment
from ...tags.tag__output import TagOUTPUT as TagOUTPUTStandard
from ...tags.tag__end import TagEND
from ...tags.tag_assign import TagAssign as TagAssignStandard
from ...tags.tag_block import TagBlock
from ...tags.tag_break import TagBreak
from ...tags.tag_capture import TagCapture
from ...tags.tag_case import TagCase as TagCaseStandard
from ...tags.tag_comment import TagComment
from ...tags.tag_continue import TagContinue
from ...tags.tag_if import TagIf as TagIfStandard
from ...tags.tag_config import (
    TagConfig as TagConfigStandard,
    TagConfigTransformer as TagConfigTransformerStandard
)
from ...tags.tag_cycle import (
    TagCycle as TagCycleStandard,
    TagCycleTransformer as TagCycleTransformerStandard
)

tag_manager.register(TagEND)
tag_manager.register(TagBlock)
tag_manager.register(TagBreak)
tag_manager.register(TagCapture)
tag_manager.register(TagComment)
tag_manager.register(TagContinue)

@tag_manager.register
class TagCOMMENT(Tag):
    """The output tag"""
    VOID = True

    def _render(self, local_vars, global_vars):
        return ''

@tag_manager.register
class TagOUTPUT(TagOUTPUTStandard):
    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register
class TagCase(TagOUTPUT, use_parser=True):
    VOID = False
    __init__ = TagCaseStandard.__init__
    _render = TagCaseStandard._render

@v_args(inline=True)
class TagAssignTransformer(TagTransformer):
    """The transformer for tag assign"""
    def tag_assign(self, varname, output):
        # type: (str, Tree) -> Tuple[str, Tree]
        """Transform the tag_assign rule"""
        return str(varname), output

@tag_manager.register
class TagAssign(TagAssignStandard):
    BASE_GRAMMAR=BASE_GRAMMAR
    TRANSFORMER=TagAssignTransformer()

    def _render(self, local_vars, global_vars):
        varname, output = self.parsed
        output = output.render(local_vars, global_vars)
        local_vars[varname] = output
        return  ''

@v_args(inline=True)
class TagConfigTransformer(TagTransformer, TagConfigTransformerStandard):
    """The transformer for tag config"""

@tag_manager.register
class TagConfig(TagConfigStandard):

    TRANSFORMER = TagConfigTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@v_args(inline=True)
class TagCycleTransformer(TagTransformer, TagCycleTransformerStandard):
    """The transformer for tag assign"""

@tag_manager.register
class TagCycle(TagCycleStandard):
    TRANSFORMER = TagCycleTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register
class TagIf(TagIfStandard):

    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

    def _render(self, local_vars, global_vars):
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars.copy(), global_vars)

        if self.next:
            next_rendered, _ = self.next.render(local_vars,
                                                global_vars,
                                                from_elder=from_elder)
            rendered += next_rendered
        return rendered

@v_args(inline=True)
class TagElseTransformer(TagTransformer):

    NOTHING = object()

    def tag_else(self, test=NOTHING):
        return test

@tag_manager.register
class TagElse(TagIf):

    PARENT_TAGS = OptionalTags('case')
    # check this is invalid:
    # {% if ... %} {% else %} {% else if ... %} {% endif %}
    ELDER_TAGS = RequiredTags('if', 'unless', 'when', 'for',
                              'elsif', 'elif', 'else')

    START = 'tag_else'
    GRAMMAR = 'tag_else: ("if" test)?'
    TRANSFORMER = TagElseTransformer()

    def _render(self, local_vars, global_vars):
        if self.parsed is TagElseTransformer.NOTHING:
            return self._render_children(local_vars.copy(), global_vars)

        return super()._render(local_vars, global_vars)

@tag_manager.register
class TagUnless(TagIf):

    def _render(self, local_vars, global_vars):
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if not expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars.copy(), global_vars)
        if self.next:
            next_rendered, _ = self.next.render(local_vars,
                                                global_vars,
                                                from_elder=from_elder)
            rendered += next_rendered
        return rendered
