from .transformer import TagTransformer
from .inherited import tag_manager, BASE_GRAMMAR
from ...tags.transformer import render_segment
from ...tags.tag_if import TagIf as TagIfStandard

@tag_manager.register
class TagIf(TagIfStandard):
    START = 'output'
    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

    def _render(self, local_vars, global_vars):
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars, global_vars)

        if self.next:
            next_rendered, _ = self.next.render(local_vars,
                                                global_vars,
                                                from_elder=from_elder)
            rendered += next_rendered
        return rendered
