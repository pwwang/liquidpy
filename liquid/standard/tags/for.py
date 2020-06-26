"""Tag for

{% for <loop> <args> %}
...
{% endfor %}
"""
from collections import namedtuple
from lark import v_args
from ...tagmgr import register
from ...common.tagparser import Tag, TagTransformer
from ...common.tagfrag import TagFrag, TagFragConst

ForObject = namedtuple(
    'ForObject', ['itername', 'obj', 'limit', 'offset', 'reversed']
)

class TagFragFor(TagFrag):

    def render(self, envs):
        itername, expr, args = self.data
        obj = expr.render(envs)
        args = dict(args)
        limit = args.get('limit', None)
        if limit:
            limit = limit.render(envs)
        offset = args.get('offset', None)
        if offset:
            offset = offset.render(envs)
        rvsed = args.get('reversed', False)
        if rvsed:
            rvsed = rvsed.render(envs)
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
        return TagFragFor((itername, expr, args))


@register
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

    def _render(self, envs):
        rendered = ''
        forobj = self.frag_rendered
        for var in forobj.obj:
            envs[forobj.itername] = var
            print(envs)
            rendered += self._children_rendered(envs)
        if not forobj.obj:
            next_rendered, _ = self.next.render(envs)
            rendered += next_rendered
        return rendered
