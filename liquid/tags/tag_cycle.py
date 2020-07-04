"""Tag cycle

{% for <loop> <args> %}
...
    {% cycle "one", "two", "three" %}
...
{% endfor %}
"""
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render

@register_tag
class TagCycle(Tag):
    """Class for for tag"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_cycle
    !tag_cycle: $tagnames [atom ":"] filter_args
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._group = None
        self._args = None

    def t_tag_cycle(self, tagname, group, colon, args=None):
        if args is None:
            args = colon
        return TagCycle(tagname, [group, args, 0])

    def group(self, local_envs, global_envs):
        if self._group is None:
            self._group = try_render(self.data[0], local_envs, global_envs)
        return self._group

    def args(self, local_envs, global_envs):
        if self._args is None:
            self._args = [try_render(arg, local_envs, global_envs)
                          for arg in self.data[1]]
        return self._args

    def get_value(self, local_envs, global_envs):
        group = self.group(local_envs, global_envs)
        args = self.args(local_envs, global_envs)
        at = self.data[2]

        ret = args[at % len(args)]
        self.data[2] = at + 1
        return str(ret)

    def _render(self, local_envs, global_envs):
        parent = self._cloest_parent('for')
        group = self.group(local_envs, global_envs)
        args = self.args(local_envs, global_envs)

        if group not in parent.cycles:
            parent.cycles[group] = self
        elif parent.cycles[group].args(local_envs, global_envs) != args:
            raise ValueError('Different arguments for cycle under '
                             f'the same group: {group}')

        return self.get_value(local_envs, global_envs)
