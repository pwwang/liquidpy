"""Tag __OUTPUT__

{{x}}
{{x | filter}}
{{x | filter: args}}
"""
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer

@v_args(inline=True)
class TransformerOutput(TagTransformer):
    """Transformer for fragment parsing output tag"""
    expr = TagTransformer.tags__expr
    expr_filter = TagTransformer.tags__expr_filter
    output = TagTransformer.tags__output

@register_tag('__OUTPUT__')
class TagOutput(Tag):
    """Class for if tag"""
    VOID = True

    SYNTAX = r"""
    start: output

    %import .tags (output, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerOutput

    def _render(self, local_envs, global_envs):
        return str(self.frag_rendered)
