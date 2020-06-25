from lark import v_args, Lark, Transformer as LarkTransformer

@v_args(inline=True)
class TagTransformer(LarkTransformer):

    def start(self, node):
        return node

class Tag:
    VOID = False
    CHILDREN = []
    PARENT = None
    SYNTAX = None
    TRANSFORMER = TagTransformer
    FROZEN = True

    def __init__(self, tagname, tagargs):
        self.name = tagname
        self.envs = {}
        self.tagargs = tagargs

    def _children_rendered(self, envs):
        rendered = []
        for child in self.CHILDREN:
            child_rendered, envs = child.render(envs)
            rendered.extend(child_rendered)
        return rendered

    def parse(self):
        parser = Lark(self.SYNTAX, parser='earley')
        tree = parser.parse(self.tagargs)
        print(tree.pretty())
        return self.TRANSFORMER().transform(tree)

    def render(self, envs=None):
        pass

    def __repr__(self):
        tagargs = str(self.tagargs)
        shortened_tagargs = (
            tagargs[:17] + '...'
            if len(tagargs) > 20
            else tagargs
        )
        return (f'<Tag(name={self.name}, '
                f'tagargs={shortened_tagargs!r}, '
                f'children={len(self.CHILDREN)})>')

class TagParsed:

    def __init__(self, parsed):
        self.parsed = parsed

    def render(self, envs=None):
        pass

class TagParsedLiteral(TagParsed):

    def render(self, envs=None):
        return self.parsed.splitlines()

class TagParsedVar(TagParsed):

    def render(self, envs=None):
        envs = envs or {}
        return envs[str(self.parsed)]

class TagParsedConst(TagParsed):

    def render(self, envs=None):
        return self.parsed

class TagParsedOpComparison(TagParsed):

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def render(self, envs=None):
        left = self.left.render(envs)
        right = self.right.render(envs)
        if self.op == '==':
            return left == right
        if self.op in ('!=', '<>'):
            return left != right
        if self.op == '<':
            return left < right
        if self.op == '>':
            return left > right
        if self.op == '<=':
            return left <= right
        if self.op == '>=':
            return left >= right
        if self.op == 'contains':
            return right in left
        if self.op == 'and':
            return left and right
        if self.op == 'or':
            return left or right

class TagParsedGetItem(TagParsed):

    def __init__(self, obj, subscript):
        self.obj = obj
        self.subscript = subscript

    def render(self, envs=None):
        envs = envs or {}
        obj = self.obj.render(envs)
        subscript = self.subscript.render(envs)

        return obj[subscript]

class TagParsedGetAttr(TagParsedGetItem):

    def render(self, envs=None):
        envs = envs or {}
        obj = self.obj.render(envs)
        subscript = str(self.subscript)

        try:
            return getattr(obj, subscript)
        except AttributeError as attr_ex:
            try:
                return obj[subscript]
            except KeyError:
                raise attr_ex
