"""Tag decrement

{% decrement my_counter %}
{% decrement my_counter %}
{% decrement my_counter %}
"""
from ...tagmgr import register_tag
from .increment import TagIncrement

@register_tag
class TagDecrement(TagIncrement):

    def _render(self, local_envs, global_envs):
        # Variables created through the decrement tag are independent
        # from variables created through assign or capture.
        var = f'__decremental__{self.data}'
        value = local_envs.get(var, -1)
        local_envs[var] = value - 1
        return str(value)
