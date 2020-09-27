"""The root tag"""
from .manager import tag_manager
from .tag import Tag
from ..config import LIQUID_LOG_INDENT
from ..utils import logger
from ..exceptions import LiquidSyntaxError

@tag_manager.register
class TagROOT(Tag):
    """The root tag as a container of all child tags"""
    def parse(self, force=False): # pylint: disable=unused-argument
        # type: (bool) -> None
        """Exclude block tags from parsing, until they are replaced"""
        if not self.parser.visitor.has_mother:
            return

        root_children = []
        # pylint: disable=access-member-before-definition
        for child in self.children:
            if child.name in ('LITERAL', 'block'):
                continue
            if child is self or child.name in ('extends', 'config', 'comment'):
                root_children.append(child)
            else:
                # don't put block back in, they replace mother's
                # and don't need to be rendered by current parser
                # (will be rendered mother parser)
                raise LiquidSyntaxError(
                    f'Tag not allowed in a sub-template: {self!r}',
                    child.context, child.parser
                )
        # pylint: disable=attribute-defined-outside-init
        self.children = root_children

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        return self._render_children(local_vars, global_vars)

    # pylint: disable=unused-argument
    def render(self, local_vars, global_vars, from_elder=False):
        # type: (dict, dict, bool) -> Tuple[str, dict]
        """Render the children of root"""
        logger.debug('%s- RENDERING %r',
                     (self.context.level) * LIQUID_LOG_INDENT,
                     self)
        # get logger back
        self.parser.config.update_logger()
        return str(self._render(local_vars, global_vars)), local_vars
