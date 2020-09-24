"""Tag assign

```liquid
{% assign x = 1 %}
{% assign x = x | plus: 1 %}
```
"""
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .transformer import TagTransformer

@v_args(inline=True)
class TagAssignTransformer(TagTransformer):
    """The transformer for tag assign"""
    def tag_assign(self, varname, output):
        # type: (str, Tree) -> Tuple[str, Tree]
        """Transform the tag_assign rule"""
        return str(varname), output

@tag_manager.register
class TagAssign(Tag):
    """The assign tag"""
    VOID = True
    START = 'tag_assign'
    GRAMMAR = 'tag_assign: varname "=" output'
    TRANSFORMER = TagAssignTransformer()

    def _render(self, local_vars, global_vars):
        varname, output = self.parsed
        output = output.render(local_vars, global_vars)
        local_vars[varname] = global_vars[varname] = output
        return  ''
