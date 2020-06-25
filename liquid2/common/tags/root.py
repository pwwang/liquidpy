from ..tagmgr import register_tag
from ..tagparser import Tag

class TagRoot(Tag):

    def render(self, **envs):
        return ''.join(self._children_rendered(envs))

register_tag('__ROOT__', TagRoot)
