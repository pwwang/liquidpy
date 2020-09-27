"""Tag tabrow

```liquid
<table>
{% tablerow product in collection.products %}
  {{ product.title }}
{% endtablerow %}
</table>
```
"""

from collections import namedtuple
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .tag_for import TagForTransformer
from .transformer import render_segment


TablerowObject = namedtuple( # pylint: disable=invalid-name
    'TablerowObject',
    ['itername', 'obj', 'limit', 'offset', 'cols']
) # type: NamedTuple

@v_args(inline=True)
class TagTablerowTransformer(TagForTransformer):
    """The transformer for tablerow tag"""
    # pylint: disable=no-self-use
    def tablerow_cols_arg(self, token):
        """Transform rule: tablerow_cols_arg"""
        return ('cols', token)

    def tag_tablerow(self, varname, atom, *args):
        """Transform rule: tag_tablerow"""
        return str(varname), atom, args


@tag_manager.register
class TagTablerow(Tag):
    """The tablerow tag"""
    GRAMMAR = '''
    tag_tablerow: NAME "in" atom tablerow_args*
    ?tablerow_args: for_limit_arg | for_offset_arg | tablerow_cols_arg
    for_limit_arg: "limit" ":" (number|var)
    for_offset_arg: "offset" ":" (number|var)
    tablerow_cols_arg: "cols" ":" (number|var)
    '''
    TRANSFORMER = TagTablerowTransformer()
    START = 'tag_tablerow'


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # pylint: disable=too-many-locals
        rendered = ''

        itername, expr, args = self.parsed
        obj = expr.render(local_vars, global_vars)
        args = dict(args)

        limit = args.get('limit', None)
        if limit:
            limit = render_segment(limit, local_vars, global_vars)

        offset = args.get('offset', None)
        if offset:
            offset = render_segment(offset, local_vars, global_vars)

        cols = args.get('cols', None)
        if cols:
            cols = render_segment(cols, local_vars, global_vars)

        if offset is not None and limit is not None:
            obj = obj[offset : (offset + limit)]
        elif offset is not None:
            obj = obj[offset:]
        elif limit is not None:
            obj = obj[:limit]

        # make it avaiable for generators
        obj = list(obj)
        lenobj = len(obj)

        cols = cols or lenobj
        # chunks
        rows = [obj[i:i + cols] for i in range(0, lenobj, cols)]
        local_vars_inside = local_vars.copy()
        for i, row in enumerate(rows):
            rendered += f'<tr class="row{i+1}">'
            for j, col in enumerate(row):
                local_vars_inside[itername] = col
                rendered += f'<td class="col{j+1}">'
                rendered += self._render_children(local_vars_inside,
                                                  global_vars)
                rendered += '</td>'

            rendered += '</tr>'

        return rendered
