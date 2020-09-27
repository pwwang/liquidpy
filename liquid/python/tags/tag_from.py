"""Tag from"""
from .inherited import tag_manager, Tag

@tag_manager.register
class TagFrom(Tag):
    """Import submodules from python"""
    VOID = True
    SECURE = False

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # pylint: disable=exec-used
        exec(f'from {self.content}', global_vars, local_vars)
        return ''
