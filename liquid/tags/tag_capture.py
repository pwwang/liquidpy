"""Tag capture
{% capture my_variable %}
I am being captured.
{% endcapture %}
"""
from ..tagmgr import register_tag
from ..tag import Tag

@register_tag
class TagCapture(Tag):
    """Class for capture tag"""

    SYNTAX = r"""
    inner_tag: tag_capture
    !tag_capture: $tagnames VAR
    """

    def t_tag_capture(self, tagname, varname):
        return TagCapture(tagname, varname)

    def _render(self, local_envs, global_envs):
        var = str(self.data)
        child = self._children_rendered(local_envs, global_envs)
        local_envs[var] = global_envs[var] = child
        return ''
