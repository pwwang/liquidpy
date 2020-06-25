from ..tagmgr import register_tag
from ..tagparser import Tag

class TagLiteral(Tag):
    VOID = True

    def parse(self):
        pass

    def render(self, envs=None):
        envs = envs or {}
        return str(self.tagargs).splitlines(), envs


register_tag('__LITERAL__', TagLiteral)
