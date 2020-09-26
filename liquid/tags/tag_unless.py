"""Tag unless

```liquid
{% unless condition %}
...
{% endunless %}
```
"""
from .manager import tag_manager
from .tag_if import TagIf

@tag_manager.register
class TagUnless(TagIf, use_parser=True):
    """The unless tag"""
    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        rendered = ''

        expr = self._render_expr(local_vars, global_vars)

        # from_elder = True
        if not expr:
            # don't go next
            # from_elder = False
            rendered += self._render_children(local_vars, global_vars)
        # {% else %} not supported in standard mode
        # if self.next:
        #    rendered += self._render_next(local_vars, global_vars, from_elder)
        return rendered
