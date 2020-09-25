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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # type: bool
        self.flag_break = False
        # type: bool
        self.flag_continue = False

    def _render(self, local_vars, global_vars):
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

        if self.next and (not value0 or not self.flag_break): # while ... else
            next_rendered, _ = self.next.render(local_vars, global_vars,
                                                from_elder=True)
            rendered += next_rendered
        return rendered
