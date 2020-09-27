"""Tag import"""
from .inherited import tag_manager, Tag

@tag_manager.register
class TagImport(Tag):
    """Tag import to import a module from python"""
    VOID = True
    SECURE = False

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        # pylint: disable=exec-used
        exec(f'import {self.content}', global_vars, local_vars)
        return ''
