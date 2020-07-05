"""Tag assign

{% assign x = 1 %}
{% assign x = x | plus: 1 %}
"""
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render

@register_tag
class TagAssign(Tag):
    """Class for if tag"""
    VOID = True

    SYNTAX = r"""
    inner_tag: tag_assign
    !tag_assign: $tagnames VAR "=" output
    """

    def t_tag_assign(self, tagname, varname, _eq, output):
        """Transformer for tag assign"""
        return TagAssign(tagname,
                         (str(varname), output))

    def _render(self, local_envs, global_envs):
        varname, output = self.data
        output = try_render(output, local_envs, global_envs)
        local_envs[varname] = global_envs[varname] = output
        return  ''
