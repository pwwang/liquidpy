"""Tag continue

// in for
{% for ... %}
...
    {% continue %}
...
{% endfor %}
"""
import importlib
from ...tagmgr import register_tag

@register_tag
class TagContinue(importlib.import_module('.break',
                                          package=__package__).TagBreak):
    """Class for tag continue"""
    def _render(self, local_envs, global_envs):
        self._cloest_parent('for').flag_continue = True
        return ''
