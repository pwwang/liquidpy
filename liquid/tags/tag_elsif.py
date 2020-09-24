"""Elsif tag

```liquid
{% if ... %}
...
{% elsif ... %}
...
[{% else %}]
...
{% endif %}
```
"""

from .manager import tag_manager
from .tag_if import TagIf
from ..utils import RequiredTags

@tag_manager.register
class TagElsif(TagIf, use_parser=True):
    """Class for tag elsif"""
    # else can be in case
    # '' indicates parent is not required
    ELDER_TAGS = RequiredTags('if', 'unless', 'elsif')
