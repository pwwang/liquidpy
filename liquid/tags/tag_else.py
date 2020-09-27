"""Else tag in following situations

```liquid
// in if
{% if ... %}
...
[{% elsif ... %}]
...
{% else %}
...
{% endif %}
// in case / when
{% case x %}
    {% when ... %}
    ...
    {% when ... %}
    ...
    {% else %}
    ...
{% endcase %}
// in for
{% for ... %}
...
{% else %}
...
{% endfor %}
```
"""

from .manager import tag_manager
from .tag import Tag
from ..utils import OptionalTags, RequiredTags
from ..exceptions import LiquidSyntaxError

@tag_manager.register
class TagElse(Tag):
    """Class for tag else"""
    # else can be in case
    # '' indicates parent is not required

    PARENT_TAGS = OptionalTags('case')
    ELDER_TAGS = RequiredTags('if', 'unless', 'when', 'for', 'elsif')

    def parse(self, force=False):
        # type: (bool) -> None
        """No extra content allowed for standard else tag"""
        if self.content:
            raise LiquidSyntaxError(f"No content allow for tag: {self!r}",
                                    self.context,
                                    self.parser)

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        return self._render_children(local_vars, global_vars)
