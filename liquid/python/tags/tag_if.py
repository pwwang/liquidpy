"""Tag if"""
from .transformer import TagTransformer
from .inherited import tag_manager, BASE_GRAMMAR
from ...tags.transformer import render_segment
from ...tags.tag_if import TagIf as TagIfStandard

@tag_manager.register
class TagIf(TagIfStandard):
    """Tag if.

    One can even do filters:
    {% if value | filter %}
    """
    START = 'output'
    TRANSFORMER = TagTransformer()
    BASE_GRAMMAR = BASE_GRAMMAR

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars, global_vars)

        rendered += self._render_next(local_vars, global_vars, from_elder)
        return rendered
