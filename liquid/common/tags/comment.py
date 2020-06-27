"""Tag comment

{% comment %}
...
{% endcomment %}
"""
from ...tagmgr import register_tag
from ..tagparser import Tag

@register_tag
class TagComment(Tag):
    """Class for tag comment"""
    SYNTAX = '<EMPTY>'

    def _render(self, local_envs, global_envs):
        return ''
