"""Else tag in following situations
// in if
{% if ... %}
...
[{% elsif ... %}]
...
{% else %}
...
{% endif %}
// in case / when
{% case x %}
    {% when ... %}
    ...
    {% when ... %}
    ...
    {% else %}
    ...
{% endcase %}
// in for
{% for ... %}
...
{% else %}
...
{% endfor %}
"""
from ..tagmgr import register_tag
from ..tag import Tag, OptionalTags, RequiredTags

@register_tag
class TagElse(Tag):
    """Class for tag else"""
    SYNTAX = r"""
    inner_tag: tag_else
    !tag_else: $tagnames
    """
    PARENT_TAGS = OptionalTags('case')
    ELDER_TAGS = RequiredTags('if', 'when', 'for', 'elsif')

    def t_tag_else(self, tagname):
        return TagElse(tagname)

    def _render(self, local_envs, global_envs):
        return self._children_rendered(local_envs, global_envs)
