"""Tag block

```liquid
{% block block1 %}
...
{% endblock %}
```
"""
from .manager import tag_manager
from .tag_capture import TagCapture

@tag_manager.register
class TagBlock(TagCapture, use_parser=True):
    """The block tag"""
    parsing_children = False

    def __repr__(self):
        # type: () -> str
        """The representation of the tag"""
        # type: str
        compact = ('both' if self.open_compact and self.close_compact
                   else 'left' if self.open_compact
                   else 'right' if self.close_compact
                   else 'none')
        return (f"<{self.__class__.__name__}"
                f"('{self.context.name}::{self.content}', "
                f"compact '{compact}', "
                f"line {self.context.lineno + 1}, "
                f"column {self.context.colno + 1})>")

    def _render(self, local_vars, global_vars):
        return self._render_children(local_vars, global_vars)
