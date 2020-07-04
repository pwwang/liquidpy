"""Tag tabrow

<table>
{% tablerow product in collection.products %}
  {{ product.title }}
{% endtablerow %}
</table>
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
class TagTablerow(Tag):
    """Class for tablerow tag"""

    SYNTAX = r"""
    inner_tag: tag_tablerow
    !tag_tablerow: $tagnames VAR "in" atom tablerow_args*
    ?tablerow_args: tablerow_limit_arg | tablerow_offset_arg | tablerow_cols_arg
    tablerow_limit_arg: "limit" ":" (int|var)
    tablerow_offset_arg: "offset" ":" (int|var)
    tablerow_cols_arg: "cols" ":" (int|var)
    """

    def t_tablerow_limit_arg(self, arg):
        return ('limit', arg)

    def t_tablerow_offset_arg(self, arg):
        return ('offset', arg)

    def t_tablerow_cols_arg(self, arg):
        return ('cols', arg)

    def t_tag_tablerow(self, tagname, varname, _in, atom, *args):
        return TagTablerow(tagname, (varname, atom, args))

    def _render(self, local_envs, global_envs):
        rendered = ''
        varname, obj, args = self.data
        obj = try_render(obj, local_envs, global_envs)
        args = dict(args)
        for key, val in args.items():
            args[key] = try_render(val, local_envs, global_envs)

        offset = args.get('offset')
        limit = args.get('limit')

        # parameters
        if offset is not None and limit is not None:
            obj = obj[offset : (offset + limit)]
        elif offset is not None:
            obj = obj[offset:]
        elif limit is not None:
            obj = obj[:limit]

        # make it avaiable for generators
        obj = list(obj)
        lenobj = len(obj)

        cols = args.get('cols', lenobj)
        # chunks
        rows = [obj[i:i + cols] for i in range(0, lenobj, cols)]
        local_envs_inside = local_envs.copy()
        for i, row in enumerate(rows):
            rendered += f'<tr class="row{i+1}">'
            for j, col in enumerate(row):
                local_envs_inside[varname] = col
                rendered += f'<td class="col{j+1}">'
                rendered += self._children_rendered(local_envs_inside,
                                                    global_envs)
                rendered += '</td>'

            rendered += '</tr>'

        return rendered
