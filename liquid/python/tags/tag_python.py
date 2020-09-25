import textwrap
from .inherited import tag_manager, Tag

@tag_manager.register
class TagPython(Tag):
    VOID = False
    SECURE = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.content:
            self.VOID = True

    def _render(self, local_vars, global_vars):
        # pylint: disable=exec-used
        if self.VOID:
            return exec(self.content, global_vars, local_vars) or ''

        children_rendered = self._render_children(local_vars, global_vars)
        return exec(textwrap.dedent(str(children_rendered)),
                    global_vars,
                    local_vars) or ''
