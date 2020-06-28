"""Tag when (in case)

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
from ...tagmgr import register_tag
from .case import TagCase

@register_tag
class TagWhen(TagCase):
    """Class for when tag"""

    PARENT_TAGS = ['case']
    PRIOR_TAGS = ['when', '']

    def _render(self, local_envs, global_envs):
        if self.frag_rendered == self.parent.frag_rendered:
            return self._children_rendered(local_envs.copy(), global_envs)
        if self.next:
            return self.next.render(local_envs, global_envs,
                                    from_prior=True)[0]
        return ''
