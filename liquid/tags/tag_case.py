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
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render
from ..exceptions import TagSyntaxError

@register_tag
class TagCase(Tag):
    """Class for case tag"""

    SYNTAX = r"""
    inner_tag: tag_case
    !tag_case: $tagnames output
    """

    def t_tag_case(self, tagname, output):
        return TagCase(tagname, output)

    def _render(self, local_envs, global_envs):
        self.data = try_render(self.data, local_envs, global_envs)
        rendered = ''
        for child in self.children:
            child_rendered, _ = child.render(local_envs, global_envs)
            rendered += child_rendered
            if child.name == 'when':
                return rendered
        raise TagSyntaxError(
            self._format_error(f'Children required in tag: {self}')
        )
