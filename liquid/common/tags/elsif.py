"""Elsif tag

{% if ... %}
...
{% elsif ... %}
...
[{% else %}]
...
{% endif %}
"""
import importlib
from ...tagmgr import register_tag

@register_tag
class TagElsif(
        importlib.import_module('.if', package=__package__).TagIf
):
    """Class for elsif tag"""

    PRIOR_TAGS = ['if', 'elsif']
