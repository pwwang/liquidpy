"""Tag case

{% assign handle = "cake" %}
{% case handle %}
  {% when "cake" %}
     This is a cake
  {% when "cookie" %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
"""
from lark import v_args
from ...tagmgr import register_tag
from ...exceptions import TagSyntaxError
from ..tagparser import Tag, TagTransformer

@v_args(inline=True)
class TransformerCase(TagTransformer):
    """Transformer for fragment parsing case tag"""
    output = TagTransformer.tags__output

@register_tag
class TagCase(Tag):
    """Class for if tag"""

    SYNTAX = r"""
    start: output

    %import .tags (output, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerCase

    def _render(self, local_envs, global_envs):
        rendered = ''
        for child in self.children:
            child_rendered, _ = child.render(local_envs, global_envs)
            rendered += child_rendered
            if child.name == 'when':
                return rendered
        raise TagSyntaxError(
            self._format_error(f'Children required in tag: {self}')
        )
