"""The parsed objects for the syntax inside a tag"""

class TagFrag:
    """Base class for parsed classes"""

    def __init__(self, data):
        """Initialize the object

        Args:
            data: The data of the parsed object
        """
        self.data = data

    def render(self, envs): # pylint: disable=unused-argument
        """Render the fragment with the given envs"""
        return self.data

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.data!r})>"

class TagFragVar(TagFrag):
    """Fragment for variables"""

    def render(self, envs):
        """Get the value of a variable from envs"""
        return envs[str(self.data)]

class TagFragConst(TagFrag):
    """Fragment for constant values"""

class TagFragOpComparison(TagFrag):
    """Comparisons with given operator"""

    def render(self, envs):
        """Get the value from the comparison"""
        left, op, right = self.data
        left = left.render(envs)
        right = right.render(envs)
        if op == '==':
            return left == right
        if op in ('!=', '<>'):
            return left != right
        if op == '<':
            return left < right
        if op == '>':
            return left > right
        if op == '<=':
            return left <= right
        if op == '>=':
            return left >= right
        if op == 'contains':
            return right in left
        if op == 'and':
            return left and right
        if op == 'or':
            return left or right

class TagFragGetItem(TagFrag):
    """Fragment for `obj[subscript]`"""

    def render(self, envs):
        """Try to get the value of the getitem operation"""
        obj, subscript = self.data
        obj = obj.render(envs)
        subscript = subscript.render(envs)

        return obj[subscript]

class TagFragGetAttr(TagFrag):
    """Fragment for `obj.attr`"""

    def render(self, envs):
        """Try to get the value of the getattr operation"""
        obj, attr = self.data
        obj = obj.render(envs)
        attr = str(attr)

        try:
            return getattr(obj, attr)
        except AttributeError as attr_ex:
            try:
                return obj[attr]
            except KeyError:
                raise attr_ex

class TagFragRange(TagFrag):
    """Fragment for range"""
    def render(self, envs):
        start, end = self.data
        start = start.render(envs)
        end = end.render(envs)

        return list(range(start, end+1))
