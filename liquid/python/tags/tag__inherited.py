"""Tags inherited from standard mode"""
# pylint: disable=relative-beyond-top-level
from lark import v_args
from .inherited import tag_manager, Tag, BASE_GRAMMAR
from .transformer import TagTransformer
from .tag_if import TagIf
from ...utils import RequiredTags
from ...tags.tag__output import TagOUTPUT as TagOUTPUTStandard
from ...tags.tag__end import TagEND
from ...tags.tag_block import TagBlock
from ...tags.tag_break import TagBreak as TagBreakStandard
from ...tags.tag_capture import TagCapture
from ...tags.tag_case import TagCase as TagCaseStandard
from ...tags.tag_comment import TagComment
from ...tags.tag_continue import TagContinue as TagContinueStandard
from ...tags.tag_extends import TagExtends
from ...tags.tag_include import TagInclude
from ...tags.tag_decrement import TagDecrement
from ...tags.tag_increment import TagIncrement
from ...tags.tag_raw import TagRaw
from ...tags.tag_when import TagWhen as TagWhenStandard
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
tag_manager.register(TagCapture)
tag_manager.register(TagComment)
tag_manager.register(TagExtends)
tag_manager.register(TagInclude)
tag_manager.register(TagDecrement)
tag_manager.register(TagIncrement)
tag_manager.register(TagRaw)

@tag_manager.register
class TagBreak(TagBreakStandard):
    """Tag break in python mode"""
    PARENT_TAGS = RequiredTags('for', 'while')
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register
class TagContinue(TagContinueStandard):
    """Tag continue in python mode"""
    PARENT_TAGS = RequiredTags('for', 'while')
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register
class TagCOMMENT(Tag):
    """The {# ... #} tag"""
    VOID = True

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # pylint: disable=unused-argument
        return ''

@tag_manager.register
class TagOUTPUT(TagOUTPUTStandard):
    """The output tag {{ ... }}"""
    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register
class TagCase(TagOUTPUT, use_parser=True):
    """The case tag"""
    VOID = False
    __init__ = TagCaseStandard.__init__
    _render = TagCaseStandard._render

@tag_manager.register
class TagWhen(TagOUTPUT, use_parser=True):
    """The when tag"""
    VOID = TagWhenStandard.VOID
    PARENT = TagWhenStandard.PARENT_TAGS
    ELDER_TAGS = TagWhenStandard.ELDER_TAGS
    _render = TagWhenStandard._render

@v_args(inline=True)
class TagConfigTransformer(TagTransformer, TagConfigTransformerStandard):
    """The transformer for tag config"""

@tag_manager.register
class TagConfig(TagConfigStandard):
    """The tag config"""
    TRANSFORMER = TagConfigTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@v_args(inline=True)
class TagCycleTransformer(TagTransformer, TagCycleTransformerStandard):
    """The transformer for tag assign"""

@tag_manager.register
class TagCycle(TagCycleStandard):
    """The tag cycle"""
    TRANSFORMER = TagCycleTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

@tag_manager.register('elif, elsif')
class TagElsif(TagIf):
    """The elif/elsif tag"""
    ELDER_TAGS = RequiredTags('if', 'unless', 'elsif', 'elif')
