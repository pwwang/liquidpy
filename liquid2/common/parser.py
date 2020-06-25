from collections import deque
from functools import wraps
from lark import v_args, Lark, Transformer as LarkTransformer
# load all shared tags
from . import tags
from .tagmgr import get_tag

def try_direct_tag(tag_transformer):
    @wraps(tag_transformer)
    def wrapper(self, *args, **kwargs):
        tag = tag_transformer(self, *args, **kwargs)
        if not self._stacks:
            self._direct_tags.append(tag)
        else:
            self._stacks[-1].CHILDREN.append(tag)
            tag.PARENT = self._stacks[-1]
        if not tag.VOID:
            self._stacks.append(tag)
        return tag
    return wrapper

@v_args(inline=True)
class Transformer(LarkTransformer):

    def __init__(self):
        super().__init__()
        self._stacks = deque()
        self._direct_tags = []

    @try_direct_tag
    def literal_tag(self, tagstr):
        return get_tag('__LITERAL__', tagstr)

    def _clean_tagstr(self, tagstr):
        tagstr = tagstr[2:-2].strip('-').strip()
        parts = tagstr.split(maxsplit=1)
        return parts.pop(0), parts[0] if parts else ''

    def start(self, *tags):
        root = get_tag('__ROOT__', None)
        root.CHILDREN = self._direct_tags
        return root

class Parser:

    GRAMMER = None
    TRANSFORMER = None


    def parse(self, template_string):
        parser = Lark(self.GRAMMER, parser='lalr')
        tree = parser.parse(template_string)
        return self.TRANSFORMER.transform(tree)
