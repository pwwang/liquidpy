"""Tag while"""
import copy
from .inherited import tag_manager
from .tag_if import TagIf
from ...tags.transformer import render_segment

@tag_manager.register
class TagWhile(TagIf):
    """The for tag

    Attributes:
        flag_break: The flag for break statement
        flag_continue: The flag for continue statement
    """
    __slots__ = TagIf.__slots__ + ('flag_break', 'flag_continue')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flag_continue = False # type: bool
        self.flag_break = False    # type: bool


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        rendered = ''
        value = render_segment(self.parsed, local_vars, global_vars)
        value0 = copy.copy(value)
        local_vars_copy = None
        while value:
            local_vars_copy = local_vars_copy or local_vars.copy()
            for child in self.children:
                child_rendered, _ = child.render(local_vars_copy, global_vars)
                rendered += child_rendered
                if self.flag_break or self.flag_continue:
                    self.flag_continue = False
                    break
            if self.flag_break:
                break

            value = render_segment(self.parsed, local_vars_copy, global_vars)

        if not value0 or not self.flag_break: # while ... else
            rendered += self._render_next(local_vars, global_vars, True)
        return rendered
