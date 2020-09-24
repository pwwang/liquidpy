"""The break tag

```liquid
{% for ... %}
    {% break %}
{% endfor %}
```
"""
from .manager import tag_manager
from .tag import Tag
from ..utils import RequiredTags
from ..exceptions import LiquidSyntaxError

@tag_manager.register
class TagBreak(Tag):
    """Class for tag break"""
    VOID = True
    PARENT_TAGS = RequiredTags('for')

    def parse(self, force=False):
        if self.content:
            raise LiquidSyntaxError(
                f"No content allow for tag: {self!r}",
                self.context, self.parser
            )

    def _render(self, local_vars, global_vars):
        self.closest_parent.flag_break = True
        return ''
