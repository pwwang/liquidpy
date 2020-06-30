"""Tag cycle

{% for <loop> <args> %}
...
    {% cycle "one", "two", "three" %}
...
{% endfor %}
"""
from varname import namedtuple
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer
from ..tagfrag import TagFrag, TagFragConst

CycleObject = namedtuple( # pylint: disable=invalid-name
    ['group', 'args', 'at']
)

class TagFragCycle(TagFrag):

    def render(self, local_envs, global_envs):
        group, args = self.data
        group = group.render(local_envs, global_envs)
        args = [arg.render(local_envs, global_envs) for arg in args]
        return CycleObject(group, args, at=[0])


@v_args(inline=True)
class TransformerCycle(TagTransformer):
    """Transformer for fragment parsing cycle tag"""
    atom = TagTransformer.tags__atom
    filter_args = TagTransformer.tags__filter_args

    def cycle_syntax(self, *args):
        if len(args) == 1:
            group, args = TagFragConst(''), args[0]
        else:
            group, args = args
        return TagFragCycle(group, args)

@register_tag
class TagCycle(Tag):
    """Class for cycle tag"""
    VOID = True
    PARENT_TAGS = ['for']
    SYNTAX = r"""
    start: cycle_syntax

    cycle_syntax: [atom ":"] filter_args

    %import .tags (atom, filter_args, WS_INLINE)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerCycle

    def _render(self, local_envs, global_envs):
        cycle = self.fragments
        parent = self._cloest_parent('for')

        group = cycle.group or str(cycle.args)

        if group not in parent.cycles:
            parent.cycles[group] = cycle
        elif parent.cycles[group].args != cycle.args:
            raise ValueError('Different arguments for cycle under '
                             f'the same group: {group}')
        cycle = parent.cycles[group]
        ret = cycle.args[cycle.at[0] % len(cycle.args)]
        cycle.at[0] += 1
        return ret
