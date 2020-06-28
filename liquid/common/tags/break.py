"""Tag break

// in for
{% for ... %}
...
    {% break %}
...
{% endfor %}
"""

from ...tagmgr import register_tag
from ..tagparser import Tag

@register_tag
class TagBreak(Tag):
    """Class for tag break"""
    VOID = True
    SYNTAX = '<EMPTY>'
    # must be in for
    PARENT_TAGS = ['for']

    def _render(self, local_envs, global_envs):
        self._cloest_parent('for').flag_break = True
        return ''
