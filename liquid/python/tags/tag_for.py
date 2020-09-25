from lark import v_args
from .transformer import TagTransformer
from .inherited import Tag, tag_manager
from ...tags.transformer import render_segment

@v_args(inline=True)
class TagForTransformer(TagTransformer):

    def tag_for(self, varname, *args):
        """Transformer for tag for"""
        varnames = (varname, *args[:-1])
        return tuple(str(vname) for vname in varnames), args[-1]

@tag_manager.register
class TagFor(Tag):
    """The for tag

    Attributes:
        flag_break: The flag for break statement
        flag_continue: The flag for continue statement
        cycles: The cycle object for cycle tags
    """
    START = 'tag_for'
    GRAMMAR = 'tag_for: var ("," var)* "in" test'
    TRANSFORMER = TagForTransformer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # type: bool
        self.flag_break = False
        # type: bool
        self.flag_continue = False

    def _render(self, local_vars, global_vars):
        rendered = ''

        varnames, value = self.parsed
        value = render_segment(value, local_vars, global_vars)
        local_vars_inside = local_vars.copy()
        for elem in value:
            if not isinstance(elem, (tuple, list)):
                elem = (elem,)
            for i, varname in enumerate(varnames):
                local_vars_inside[varname] = elem[i]

            for child in self.children:
                child_rendered, _ = child.render(local_vars_inside,
                                                 global_vars)
                rendered += child_rendered
                if self.flag_break or self.flag_continue:
                    self.flag_continue = False
                    break
            if self.flag_break:
                break

        if self.next and (not value or not self.flag_break): # for ... else
            next_rendered, _ = self.next.render(local_vars, global_vars,
                                                from_elder=True)
            rendered += next_rendered
        return rendered
