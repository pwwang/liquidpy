"""Tag comment
{% comment %}
...
{% endcomment %}
"""
from ..tagmgr import register_tag
from ..tag import Tag

@register_tag
class TagComment(Tag):
    """Class for tag comment"""
    SYNTAX = r"""
    inner_tag: tag_comment
    !tag_comment: $tagnames
    """

    def t_tag_comment(self, tagname):
        """Transformer for tag comment"""
        return TagComment(tagname)

    def _render(self, local_envs, global_envs):
        return ''
