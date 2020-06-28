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

        # Strings, even when empty, are truthy.
        # See: https://shopify.github.io/liquid/basics/truthy-and-falsy/#truthy
        if isinstance(self.frag_rendered, str):
            self.frag_rendered = True
        elif (self.frag_rendered not in (True, False) and
              isinstance(self.frag_rendered, (int, float))):
            self.frag_rendered = True
        elif isinstance(self.frag_rendered, (tuple, list)):
            self.frag_rendered = True

        if not self.frag_rendered:
            rendered += self._children_rendered(local_envs.copy(), global_envs)

        return rendered
