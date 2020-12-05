"""More pythonic for tag for python mode of liquidpy"""
from lark import v_args
from .transformer import TagTransformer
from .inherited import Tag, tag_manager
from ...tags.transformer import render_segment

@v_args(inline=True)
class TagForTransformer(TagTransformer):
    """Transformer for tag for"""
    # pylint: disable=no-self-use
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
    __slots__ = Tag.__slots__ + ('flag_break', 'flag_continue')

    START = 'tag_for'
    GRAMMAR = 'tag_for: var ("," var)* "in" output'
    TRANSFORMER = TagForTransformer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_break = False      # type: bool
        self.flag_continue = False   # type: bool


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
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
                if self.flag_continue or self.flag_break:
                    self.flag_continue = False
                    break
            if self.flag_break:
                break

        if not value or not self.flag_break: # for ... else
            rendered += self._render_next(local_vars, global_vars, True)
        return rendered
