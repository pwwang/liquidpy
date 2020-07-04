"""Tag when

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
from ..tag import Tag, OptionalTags, RequiredTags
from ..tagfrag import try_render

@register_tag
class TagWhen(Tag):
    """Class for when tag"""

    SYNTAX = r"""
    inner_tag: tag_when
    !tag_when: $tagnames output
    """
    PARENT_TAGS = RequiredTags('case')
    ELDER_TAGS = OptionalTags('when')

    def t_tag_when(self, tagname, output):
        return TagWhen(tagname, output)

    def _render(self, local_envs, global_envs):
        data = try_render(self.data, local_envs, global_envs)
        if data == self.parent.data:
            return self._children_rendered(local_envs.copy(), global_envs)
        if self.next:
            return self.next.render(local_envs, global_envs,
                                    from_elder=True)[0]
        return ''
