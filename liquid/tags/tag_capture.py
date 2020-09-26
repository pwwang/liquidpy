"""Tag capture

```liquid
{% capture my_variable %}
I am being captured.
{% endcapture %}
```
"""

from .manager import tag_manager
from .tag import Tag

@tag_manager.register
class TagCapture(Tag):
    """The capture tag"""

    START = 'varname' # type: str

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        var = str(self.parsed)
        child = self._render_children(local_vars, global_vars)
        local_vars[var] = global_vars[var] = child

        return ''
