"""Tag if

{% if condition %}
...
{% endif %}
"""
from lark import v_args
from ...tagmgr import register
from ...common.tagparser import Tag, TagTransformer

@v_args(inline=True)
class TransformerIf(TagTransformer):
    """Transformer for fragment parsing if if tag"""
    expr = TagTransformer.tags__expr

@register
class TagIf(Tag):
    """Class for if tag"""
    SYNTAX = r"""
    start: expr

    %import .tags (expr, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerIf

    def _render(self, envs):
        rendered = ''
        if self.frag_rendered:
            self.next = None
            rendered += self._children_rendered(envs)
        if self.next:
            next_rendered, _ = self.next.render(envs)
            rendered += next_rendered
        return rendered
