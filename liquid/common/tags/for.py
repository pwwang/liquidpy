"""Tag for

{% for <loop> <args> %}
...
{% endfor %}
"""
from varname import namedtuple
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer
from ..tagfrag import TagFrag, TagFragConst

ForObject = namedtuple( # pylint: disable=invalid-name
    ['itername', 'obj', 'limit', 'offset', 'reversed']
)
ForLoop = namedtuple( # pylint: disable=invalid-name
    ['first', 'index', 'index0', 'last',
     'length', 'rindex', 'rindex0']
)

class TagFragFor(TagFrag):

    def render(self, local_envs, global_envs):
        itername, expr, args = self.data
        obj = expr.render(local_envs, global_envs)
        args = dict(args)
        limit = args.get('limit', None)
        if limit:
            limit = limit.render(local_envs, global_envs)
        offset = args.get('offset', None)
        if offset:
            offset = offset.render(local_envs, global_envs)
        rvsed = args.get('reversed', False)
        if rvsed:
            rvsed = rvsed.render(local_envs, global_envs)
        return ForObject(str(itername), obj, limit, offset, rvsed)


@v_args(inline=True)
class TransformerFor(TagTransformer):
    """Transformer for fragment parsing for tag"""
    atom = TagTransformer.tags__atom
    var = TagTransformer.tags__var
    number = TagTransformer.tags__number

    def args(self, token):
        return token

    def limit_arg(self, token):
        return ('limit', token)

    def offset_arg(self, token):
        return ('offset', token)

    def reversed_arg(self, token):
        return ('reversed', TagFragConst(bool(token)))

    def iter(self, itername):
        return itername

    def for_syntax(self, itername, expr, *args):
        return TagFragFor(itername, expr, args)


@register_tag
class TagFor(Tag):
    """Class for if tag"""
    SYNTAX = r"""
    start: for_syntax

    for_syntax: iter "in" atom args*
    iter: VAR

    ?args: limit_arg | offset_arg | reversed_arg
    limit_arg: "limit" ":" (number|var)
    offset_arg: "offset" ":" (number|var)
    !reversed_arg: "reversed"

    %import .tags (var, atom, number, WS_INLINE, VAR)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerFor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_break = False
        self.flag_continue = False
        self.cycles = {}

    def _render(self, local_envs, global_envs):
        rendered = ''
        forobj = self.fragments
        # parameters
        obj = forobj.obj
        if forobj.offset is not None and forobj.limit is not None:
            obj = forobj.obj[
                forobj.offset : (forobj.offset + forobj.limit)
            ]
        elif forobj.offset is not None:
            obj = forobj.obj[forobj.offset:]
        elif forobj.limit is not None:
            obj = forobj.obj[:forobj.limit]

        if forobj.reversed:
            obj = reversed(obj)

        obj = list(obj)
        print(obj)
        # make it avaiable for generators
        forlen = len(obj)
        local_envs_inside = local_envs.copy()
        for i, var in enumerate(obj):
            local_envs_inside[forobj.itername] = var
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
                                                from_prior=True)
            rendered += next_rendered
        return rendered
