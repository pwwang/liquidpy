"""The end tag

```liquid
{% endxxx %}
```
"""
from .manager import tag_manager
from .tag import Tag

@tag_manager.register
class TagEND(Tag):
    """End tag: '{% endxxx %}'"""
