"""Tag assign

{% assign x = 1 %}
{% assign x = x | plus: 1 %}
"""
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer
from ..tagfrag import TagFrag

class TagFragAssign(TagFrag):

    def render(self, local_envs, global_envs):
        varname, value = self.data
        varname = str(varname)
        value = value.render(local_envs, global_envs)
        global_envs[varname] = value

@v_args(inline=True)
class TransformerAssign(TagTransformer):
    """Transformer for fragment parsing assign tag"""
    output = TagTransformer.tags__output

    def assign(self, varname, value):
        return TagFragAssign(varname, value)

@register_tag
class TagAssign(Tag):
    """Class for if tag"""
    VOID = True

    SYNTAX = r"""
    start: assign

    assign: VAR "=" output

    %import .tags (VAR, output, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerAssign

    def _render(self, local_envs, global_envs):
        return ''
