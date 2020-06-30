"""Tag capture

{% capture my_variable %}
I am being captured.
{% endcapture %}
"""
from ...tagmgr import register_tag
from ..tagparser import Tag

@register_tag
class TagCapture(Tag):
    """Class for if tag"""
    VOID = False
    PARSING = False

    SYNTAX = r"""
    start: varname

    varname: VAR

    %import .tags (VAR, WS_INLINE)
    %ignore WS_INLINE
    """

    def _render(self, local_envs, global_envs):
        var = str(self.data)
        child = self._children_rendered(local_envs, global_envs)
        local_envs[var] = global_envs[var] = child
        return ''
