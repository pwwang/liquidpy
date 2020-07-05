"""Tag elsif
{% if condition %}
...
{% elsif ... %}
...
{% endif %}
"""
from ..tagmgr import register_tag
from ..tag import RequiredTags
from .tag_if import TagIf

@register_tag
class TagElsif(TagIf):
    """Class for if tag"""

    SYNTAX = r"""
    inner_tag: tag_elsif
    !tag_elsif: $tagnames expr
    """
    ELDER_TAGS = RequiredTags('if', 'unless', 'elsif')

    def t_tag_elsif(self, tagname, expr):
        """Transformer for tag elsif"""
        return TagElsif(tagname, expr)
