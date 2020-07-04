"""Tag unless
{% unless condition %}
...
{% endunless %}
"""
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render

@register_tag
class TagUnless(Tag):
    """Class for unless tag"""

    SYNTAX = r"""
    inner_tag: tag_unless
    !tag_unless: $tagnames expr
    """

    def t_tag_unless(self, tagname, expr):
        return TagUnless(tagname, expr)

    def _render(self, local_envs, global_envs):
        rendered = ''

        expr = try_render(self.data, local_envs, global_envs)

        # Strings, even when empty, are truthy.
        # See: https://shopify.github.io/liquid/basics/truthy-and-falsy/#truthy
        if isinstance(expr, str):
            expr = True
        elif (expr not in (True, False) and
              isinstance(expr, (int, float))):
            expr = True
        elif isinstance(expr, (tuple, list)):
            expr = True

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
