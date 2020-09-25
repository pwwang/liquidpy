from .inherited import tag_manager
from .tag_if import TagIf
from ...tags.transformer import render_segment

@tag_manager.register
class TagUnless(TagIf, use_parser=True):

    def _render(self, local_vars, global_vars):
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if not expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars, global_vars)

        if self.next:
            next_rendered, _ = self.next.render(local_vars,
                                                global_vars,
                                                from_elder=from_elder)
            rendered += next_rendered
        return rendered
