"""Tag increment

{% increment my_counter %}
{% increment my_counter %}
{% increment my_counter %}
"""
from ..tagmgr import register_tag
from ..tag import Tag

@register_tag
class TagIncrement(Tag):
    """Class for tag increment"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_increment
    !tag_increment: $tagnames VAR
    """

    def t_tag_increment(self, tagname, var):
        """Transformer for tag increment"""
        return TagIncrement(tagname, var)

    def _render(self, local_envs, global_envs):
        # Variables created through the increment tag are independent
        # from variables created through assign or capture.
        var = f'__incremental__{self.data}'
        value = local_envs.get(var, 0)
        local_envs[var] = value + 1
        return str(value)
