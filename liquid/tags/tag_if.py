"""Tag if

```liquid
{% if condition %}
...
{% endif %}
```
"""

from .manager import tag_manager
from .tag import Tag
from .transformer import render_segment
from ..filters import EmptyDrop

@tag_manager.register
class TagIf(Tag):

    START = 'test'

    def _render(self, local_vars, global_vars):
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)

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
