"""Tag tabrow

<table>
{% tablerow product in collection.products %}
  {{ product.title }}
{% endtablerow %}
</table>
"""
import importlib
from varname import namedtuple
from lark import v_args
from ...tagmgr import register_tag
from ..tagparser import Tag, TagTransformer
from ..tagfrag import TagFrag, TagFragConst

# tagfor module, we cannot do: from . import for
# since for is a keyword
tagfor = importlib.import_module('.for', package=__package__)

TablerowObject = namedtuple( # pylint: disable=invalid-name
    ['itername', 'obj', 'limit', 'offset', 'cols']
)

class TagFragTablerow(TagFrag):

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

        cols = args.get('cols', None)
        if cols:
            cols = cols.render(local_envs, global_envs)

        return TablerowObject(str(itername), obj, limit, offset, cols)


@v_args(inline=True)
class TransformerTablerow(tagfor.TransformerFor):
    """Transformer for fragment parsing tablerow tag"""

    def cols_arg(self, token):
        return ('cols', token)

    def iter(self, itername):
        return itername

    def tablerow_syntax(self, itername, expr, *args):
        return TagFragTablerow(itername, expr, args)


@register_tag
class TagTablerow(Tag):
    """Class for if tag"""
    SYNTAX = r"""
    start: tablerow_syntax

    tablerow_syntax: iter "in" atom args*
    iter: VAR

    ?args: limit_arg | offset_arg | cols_arg
    limit_arg: "limit" ":" (number|var)
    offset_arg: "offset" ":" (number|var)
    cols_arg: "cols" ":" (number|var)

    %import .tags (var, atom, number, WS_INLINE, VAR)
    %ignore WS_INLINE
    """

    TRANSFORMER = TransformerTablerow

    def _render(self, local_envs, global_envs):
        rendered = ''
        trobj = self.frag_rendered
        # parameters
        obj = trobj.obj
        if trobj.offset is not None and trobj.limit is not None:
            obj = trobj.obj[
                trobj.offset : (trobj.offset + trobj.limit)
            ]
        elif trobj.offset is not None:
            obj = trobj.obj[trobj.offset:]
        elif trobj.limit is not None:
            obj = trobj.obj[:trobj.limit]

        # make it avaiable for generators
        obj = list(obj)
        lenobj = len(obj)

        cols = trobj.cols or lenobj
        # chunks
        rows = [obj[i:i + cols] for i in range(0, lenobj, cols)]
        local_envs_inside = local_envs.copy()
        for i, row in enumerate(rows):
            rendered += f'<tr class="row{i+1}">'
            for j, col in enumerate(row):
                local_envs_inside[trobj.itername] = col
                rendered += f'<td class="col{j+1}">'
                rendered += self._children_rendered(local_envs_inside,
                                                    global_envs)
                rendered += '</td>'

            rendered += '</tr>'

        return rendered
