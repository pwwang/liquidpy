"""Tag if

{% if condition %}
...
{% endif %}
"""
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer

@v_args(inline=True)
class TransformerIf(TagTransformer):
    """Transformer for fragment parsing if if tag"""
    expr = TagTransformer.tags__expr

@register_tag
class TagIf(Tag):
    """Class for if tag"""
    SYNTAX = r"""
    start: expr

    %import .tags (expr, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerIf

    def _render(self, local_envs, global_envs):
        rendered = ''

        if self.frag_rendered:
            self.next = None
            rendered += self._children_rendered(local_envs.copy(), global_envs)
        if self.next:
            next_rendered, _ = self.next.render(local_envs, global_envs)
            rendered += next_rendered
        return rendered
