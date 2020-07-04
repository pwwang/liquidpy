"""Tag break

// in for
{% for ... %}
...
    {% break %}
...
{% endfor %}
"""
from ..tagmgr import register_tag
from ..tag import Tag, RequiredTags

@register_tag
class TagBreak(Tag):
    """Class for tag break"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_break
    !tag_break: $tagnames
    """
    PARENT_TAGS = RequiredTags('for')

    def t_tag_break(self, tagname):
        return TagBreak(tagname)

    def _render(self, local_envs, global_envs):
        self._cloest_parent('for').flag_break = True
        return ''
