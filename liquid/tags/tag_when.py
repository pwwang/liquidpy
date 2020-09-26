"""Tag when (in case)

```liquid
{% assign handle = "cake" %}
{% case handle %}
  {% when "cake" %}
     This is a cake
  {% when "cookie" %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
```
"""
from .manager import tag_manager
from .tag__output import TagOUTPUT
from ..utils import RequiredTags, OptionalTags

@tag_manager.register
class TagWhen(TagOUTPUT, use_parser=True):
    """The when tag"""
    VOID = False

    PARENT_TAGS = RequiredTags('case')
    ELDER_TAGS = OptionalTags('when')

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        data = self.PARSER.parse(self.content).render(local_vars, global_vars)
        if data == self.closest_parent.data:
            return self._render_children(local_vars, global_vars)
        return self._render_next(local_vars, global_vars, True)
