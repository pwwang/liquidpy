"""Else tag in following situations
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
"""

from ...tagmgr import register
from ...common.tagparser import Tag

@register
class TagElse(Tag):
    """Class for tag else"""
    SYNTAX = '<EMPTY>'
    # else can be in case
    # '' indicates parent is not required
    PARENT_TAGS = ['case', '']
    PRIOR_TAGS = ['if', 'when', 'for', 'elsif']

    def _render(self, envs):
        return self._children_rendered(envs)
