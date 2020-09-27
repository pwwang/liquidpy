"""Tag for

```liquid
{% for <loop> <args> %}
...
{% endfor %}
```
"""

from collections import namedtuple
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .transformer import TagTransformer, render_segment


ForLoop = namedtuple( # pylint: disable=invalid-name
    'ForLoop',
    ['first', 'index', 'index0', 'last',
     'length', 'rindex', 'rindex0']
)

@v_args(inline=True)
class TagForTransformer(TagTransformer):
    """The transformer for tag for"""
    # pylint: disable=no-self-use
    def for_limit_arg(self, arg):
        """Transformer for for_limit_arg"""
        return ('limit', arg)

    def for_offset_arg(self, arg):
        """Transformer for for_offset_arg"""
        return ('offset', arg)

    def for_reversed_arg(self):
        """Transformer for for_reversed_arg"""
        return ('reversed', True)

    def tag_for(self, varname, atom, *args):
        """Transformer for tag for"""
        return str(varname), atom, args

@tag_manager.register
class TagFor(Tag):
    """The for tag

    Attributes:
        flag_break: The flag for break statement
        flag_continue: The flag for continue statement
        cycles: The cycle object for cycle tags
    """
    __slots__ = Tag.__slots__ + ('flag_break', 'flag_continue', 'cycles')

    START = 'tag_for'
    GRAMMAR = '''
    tag_for: varname "in" atom for_args*
    ?for_args: for_limit_arg | for_offset_arg | for_reversed_arg
    for_limit_arg: "limit" ":" (number|var)
    for_offset_arg: "offset" ":" (number|var)
    for_reversed_arg: "reversed"
    '''
    TRANSFORMER = TagForTransformer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_break = False      # type: bool
        self.flag_continue = False   # type: bool
        self.cycles = {}             # type: Dict[str, TagCycle]


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # pylint: disable=too-many-locals
        rendered = ''

        varname, atom, args = self.parsed
        obj = render_segment(atom, local_vars, global_vars)
        forargs = {'limit': None, 'offset': None, 'reversed': False}
        for argname, argvalue in args:
            argvalue = render_segment(argvalue, local_vars, global_vars)
            forargs[str(argname)] = argvalue

        # parameters
        if forargs['limit'] is not None and forargs['offset'] is not None:
            obj = obj[
                forargs['offset'] : (forargs['offset'] + forargs['limit'])
            ]
        elif forargs['offset'] is not None:
            obj = obj[forargs['offset']:]
        elif forargs['limit'] is not None:
            obj = obj[:forargs['limit']]

        if forargs['reversed']:
            obj = reversed(obj)

        # make it avaiable for generators
        obj = list(obj)

        forlen = len(obj)
        local_vars_inside = local_vars.copy()
        for i, var in enumerate(obj):
            local_vars_inside[varname] = var
            # forloop object
            local_vars_inside['forloop'] = ForLoop(
                first=i == 0,
                index=i + 1,
                index0=i,
                last=i == forlen - 1,
                length=forlen,
                rindex=forlen - i,
                rindex0=forlen - i - 1
            )
            for child in self.children:
                child_rendered, _ = child.render(local_vars_inside,
                                                 global_vars)
                rendered += child_rendered
                if self.flag_break or self.flag_continue:
                    self.flag_continue = False
                    break
            if self.flag_break:
                break

        if not obj:
            rendered += self._render_next(local_vars, global_vars, True)
        return rendered
