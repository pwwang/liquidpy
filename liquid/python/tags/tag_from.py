from .inherited import tag_manager, Tag

@tag_manager.register
class TagFrom(Tag):
    VOID = True
    SECURE = False

    def _render(self, local_vars, global_vars):
        # pylint: disable=exec-used
        exec(f'from {self.content}', global_vars, local_vars)
        return ''
