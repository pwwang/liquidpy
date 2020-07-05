"""Tag unless
{% unless condition %}
...
{% endunless %}
"""
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render
from ..filters import EmptyDrop

@register_tag
class TagUnless(Tag):
    """Class for unless tag"""

    SYNTAX = r"""
    inner_tag: tag_unless
    !tag_unless: $tagnames expr
    """

    def t_tag_unless(self, tagname, expr):
        """Transformer for tag unless"""
        return TagUnless(tagname, expr)

    def _render(self, local_envs, global_envs):
        rendered = ''

        expr = try_render(self.data, local_envs, global_envs)

        # Strings, even when empty, are truthy.
        # See: https://shopify.github.io/liquid/basics/truthy-and-falsy/#truthy
        if isinstance(expr, str):
            expr = True
        elif (isinstance(expr, (int, float)) and
              expr is not True and
              expr is not False):
            expr = True
        elif isinstance(expr, EmptyDrop):
            expr = False

        from_elder = True
        if not expr:
            # don't go next
            from_elder = False
            rendered += self._children_rendered(local_envs.copy(), global_envs)
        if self.next:
            next_rendered, _ = self.next.render(local_envs,
                                                global_envs,
                                                from_elder=from_elder)
            rendered += next_rendered
        return rendered
