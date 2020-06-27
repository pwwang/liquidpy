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
    """Transformer for fragment parsing if if tag"""
    expr = TagTransformer.tags__expr
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

    for_syntax: iter "in" expr args*
    iter: VAR

    ?args: limit_arg | offset_arg | reversed_arg
    limit_arg: "limit" ":" (number|var)
    offset_arg: "offset" ":" (number|var)
    !reversed_arg: "reversed"

    %import .tags (var, expr, number, WS_INLINE, VAR)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerFor

    def _render(self, local_envs, global_envs):
        rendered = ''
        forobj = self.frag_rendered
        local_envs_inside = local_envs.copy()
        for var in forobj.obj:
            local_envs_inside[forobj.itername] = var
            rendered += self._children_rendered(local_envs_inside, global_envs)
        if not forobj.obj:
            next_rendered, _ = self.next.render(local_envs, global_envs)
            rendered += next_rendered
        return rendered
