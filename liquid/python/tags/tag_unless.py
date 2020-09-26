"""Tag unless"""
from .inherited import tag_manager
from .tag_if import TagIf
from ...tags.transformer import render_segment

@tag_manager.register
class TagUnless(TagIf, use_parser=True):
    """Tag unless, with no emptydrop stuff"""
    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        rendered = ''

        expr = render_segment(self.parsed, local_vars, global_vars)
        from_elder = True
        if not expr:
            # don't go next
            from_elder = False
            rendered += self._render_children(local_vars, global_vars)

        rendered += self._render_next(local_vars, global_vars, from_elder)
        return rendered
