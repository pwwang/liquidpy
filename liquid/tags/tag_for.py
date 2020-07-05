"""Tag for

{% for <loop> <args> %}
...
{% endfor %}
"""
from varname import namedtuple
from ..tagmgr import register_tag
from ..tag import Tag
from ..tagfrag import try_render

ForLoop = namedtuple( # pylint: disable=invalid-name
    ['first', 'index', 'index0', 'last',
     'length', 'rindex', 'rindex0']
)

@register_tag
class TagFor(Tag):
    """Class for for tag"""

    SYNTAX = r"""
    inner_tag: tag_for
    !tag_for: $tagnames VAR "in" atom for_args*
    ?for_args: for_limit_arg | for_offset_arg | for_reversed_arg
    for_limit_arg: "limit" ":" (int|var)
    for_offset_arg: "offset" ":" (int|var)
    for_reversed_arg: "reversed"
    """

    def t_for_limit_arg(self, arg):
        """Transformer for for_limit_arg"""
        return ('limit', arg)

    def t_for_offset_arg(self, arg):
        """Transformer for for_offset_arg"""
        return ('offset', arg)

    def t_for_reversed_arg(self):
        """Transformer for for_reversed_arg"""
        return ('reversed', True)

    def t_tag_for(self, tagname, varname, _in, atom, *args):
        """Transformer for tag for"""
        return TagFor(tagname, (varname, atom, args))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_break = False
        self.flag_continue = False
        self.cycles = {}

    def _render(self, local_envs, global_envs):
        rendered = ''

        varname, atom, args = self.data
        varname = str(varname)
        obj = try_render(atom, local_envs, global_envs)
        forargs = {'limit': None, 'offset': None, 'reversed': False}
        for argname, argvalue in args:
            argvalue = try_render(argvalue, local_envs, global_envs)
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
        local_envs_inside = local_envs.copy()
        for i, var in enumerate(obj):
            local_envs_inside[varname] = var
            # forloop object
            local_envs_inside['forloop'] = ForLoop(
                first=i == 0,
                index=i + 1,
                index0=i,
                last=i == forlen - 1,
                length=forlen,
                rindex=forlen - i,
                rindex0=forlen - i - 1
            )
            for child in self.children:
                child_rendered, _ = child.render(local_envs_inside,
                                                 global_envs)
                rendered += child_rendered
                if self.flag_break or self.flag_continue:
                    self.flag_continue = False
                    break
            if self.flag_break:
                break

        if not obj:
            next_rendered, _ = self.next.render(local_envs, global_envs,
                                                from_elder=True)
            rendered += next_rendered
        return rendered
