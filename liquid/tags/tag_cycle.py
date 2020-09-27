"""Tag cycle

```liquid
{% for <loop> <args> %}
...
    {% cycle "one", "two", "three" %}
...
{% endfor %}
```
"""
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .transformer import TagTransformer, render_segment
from ..utils import RequiredTags
from ..exceptions import LiquidRenderError

@v_args(inline=True)
class TagCycleTransformer(TagTransformer):
    """The transformer for tag cycle"""
    # pylint: disable=no-self-use
    def tag_cycle(self, group, args=None):
        """Transformer for tag for"""
        return [group, args, 0]

@tag_manager.register
class TagCycle(Tag):
    """The cycle tag"""
    VOID = True
    PARENT_TAGS = RequiredTags('for')

    START = 'tag_cycle'
    GRAMMAR = 'tag_cycle: [(constant|var) ":"] arguments'
    TRANSFORMER = TagCycleTransformer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group = None
        self._args = None

    def group(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        """Get the group of the cycle"""
        if self._group is None:
            self._group = render_segment(
                self.parsed[0], local_vars, global_vars
            )
        return self._group

    def args(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        """Get the args of the cycle"""
        if self._args is None:
            args, kwargs = self.parsed[1].render(local_vars, global_vars)
            if kwargs:
                raise LiquidRenderError("No keyword arguments allowed.",
                                        self.context, self.parser)
            self._args = args
        return self._args

    def get_value(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        """Get current value of the cycle, and
        increment the cursor"""
        args = self.args(local_vars, global_vars)
        at = self.parsed[2] # pylint: disable=invalid-name

        ret = args[at % len(args)]
        self.parsed[2] = at + 1
        return str(ret)

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        parent = self.closest_parent
        group = self.group(local_vars, global_vars)
        args = self.args(local_vars, global_vars)

        if group not in parent.cycles:
            parent.cycles[group] = self
        elif parent.cycles[group].args(local_vars, global_vars) != args:
            raise LiquidRenderError(
                'Different arguments for cycle under '
                f'the same group: {group}',
                self.context, self.parser
            )

        return self.get_value(local_vars, global_vars)
