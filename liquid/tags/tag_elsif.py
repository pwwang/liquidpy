"""Tag elsif
{% if condition %}
...
{% elsif ... %}
...
{% endif %}
"""
from ..tagmgr import register_tag
from ..tag import Tag, RequiredTags
from ..tagfrag import try_render
from .tag_if import TagIf

@register_tag
class TagElsif(TagIf):
    """Class for if tag"""

    SYNTAX = r"""
    inner_tag: tag_elsif
    !tag_elsif: $tagnames expr
    """
    ELDER_TAGS = RequiredTags('if', 'elsif')

    def t_tag_elsif(self, tagname, expr):
        return TagElsif(tagname, expr)
