"""The continue tag

```liquid
{% for ... %}
    {% continue %}
{% endfor %}
```
"""
from .manager import tag_manager
from .tag_break import TagBreak

@tag_manager.register
class TagContinue(TagBreak):
    """Class for tag continue"""
    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        self.closest_parent.flag_continue = True
        return ''
