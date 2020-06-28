"""Tag increment

{% increment my_counter %}
{% increment my_counter %}
{% increment my_counter %}
"""
from ...tagmgr import register_tag
from .capture import TagCapture

@register_tag
class TagIncrement(TagCapture):
    VOID = True

    def _render(self, local_envs, global_envs):
        self.parsed = None
        # Variables created through the increment tag are independent
        # from variables created through assign or capture.
        var = f'__incremental__{self.data}'
        value = local_envs.get(var, 0)
        local_envs[var] = value + 1
        return str(value)
