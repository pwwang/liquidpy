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

        frag_rendered = self.fragments
        # Strings, even when empty, are truthy.
        # See: https://shopify.github.io/liquid/basics/truthy-and-falsy/#truthy
        if isinstance(frag_rendered, str):
            frag_rendered = True
        elif (frag_rendered not in (True, False) and
              isinstance(frag_rendered, (int, float))):
            frag_rendered = True
        elif isinstance(frag_rendered, (tuple, list)):
            frag_rendered = True

        from_prior = True
        if frag_rendered:
            # don't go next
            from_prior = False
            rendered += self._children_rendered(local_envs.copy(), global_envs)
        if self.next:
            next_rendered, _ = self.next.render(local_envs,
                                                global_envs,
                                                from_prior=from_prior)
            rendered += next_rendered
        return rendered
