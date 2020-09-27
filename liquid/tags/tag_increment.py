"""Tag increment

```liquid
{% increment my_counter %}
{% increment my_counter %}
{% increment my_counter %}
```
"""

from .manager import tag_manager
from .tag_capture import TagCapture

@tag_manager.register
class TagIncrement(TagCapture, use_parser=True):
    """The increment tag"""
    VOID = True

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # Variables created through the increment tag are independent
        # from variables created through assign or capture.
        var = f'__incremental__{self.parsed}'
        value = local_vars.get(var, 0)
        local_vars[var] = value + 1
        return str(value)
