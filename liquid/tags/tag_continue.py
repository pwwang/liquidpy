"""Tag continue

// in for
{% for ... %}
...
    {% continue %}
...
{% endfor %}
"""
from ..tagmgr import register_tag
from ..tag import Tag, RequiredTags

@register_tag
class TagContinue(Tag):
    """Class for tag continue"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_continue
    !tag_continue: $tagnames
    """
    PARENT_TAGS = RequiredTags('for')

    def t_tag_continue(self, tagname):
        return TagContinue(tagname)

    def _render(self, local_envs, global_envs):
        self._cloest_parent('for').flag_continue = True
        return ''
