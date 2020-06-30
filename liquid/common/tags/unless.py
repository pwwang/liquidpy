"""Tag unless

{% unless condition %}
...
{% endif %}
"""
import importlib
from ...tagmgr import register_tag

@register_tag
class TagUnless(
        importlib.import_module('.if', package=__package__).TagIf
):

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

        if not frag_rendered:
            rendered += self._children_rendered(local_envs.copy(), global_envs)

        return rendered
