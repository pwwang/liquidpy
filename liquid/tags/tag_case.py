"""Tag case

```liquid
{% assign handle = "cake" %}
{% case handle %}
  {% when "cake" %}
     This is a cake
  {% when "cookie" %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
```
"""
from .manager import tag_manager
from .tag__output import TagOUTPUT
from ..exceptions import LiquidSyntaxError

@tag_manager.register
class TagCase(TagOUTPUT, use_parser=True):
    """The case class"""
    VOID = False # type: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        self.data = self.parsed.render(
            local_vars, global_vars
        )
        rendered = ''
        for child in self.children:
            child_rendered, _ = child.render(local_vars, global_vars)
            rendered += child_rendered
            if child.name == 'when':
                return rendered
        raise LiquidSyntaxError(
            f'No children found in tag: {self!r}',
            self.context, self.parser
        )
