"""The output tag

```liquid
{{ ... }}
```
"""
from .manager import tag_manager
from .tag import Tag

@tag_manager.register
class TagOUTPUT(Tag):
    """The output tag"""
    VOID = True
    START = 'output'

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        rendered = self.parsed.render(local_vars, global_vars)
        return str(rendered) if rendered is not None else ''
