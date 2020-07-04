"""The parsed objects for the syntax inside a tag"""

from .config import LIQUID_FILTERS_ENVNAME
from .filters import EmptyDrop

class TagFrag:
    """Base class for parsed classes"""

    def __init__(self, *data):
        """Initialize the object

        Args:
            data: The data of the parsed object
        """
        self.data = data if len(data) > 1 else data[0]

    def render(self, local_envs, global_envs): # pylint: disable=unused-argument
        """Render the fragment with the given envs"""
        return self.data

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.data!r})>"

class TagFragVar(TagFrag):
    """Fragment for variables"""

    def render(self, local_envs, global_envs):
        """Get the value of a variable from envs"""
        varname = str(self.data)
        if varname in local_envs:
            var = local_envs[varname]
        else:
            var = global_envs[varname]
        if isinstance(var, (tuple, list)) and len(var) == 0:
            return EmptyDrop()
        return var

class TagFragConst(TagFrag):
    """Fragment for constant values"""

class TagFragOpComparison(TagFrag):
    """Comparisons with given operator"""

    def render(self, local_envs, global_envs):
        """Get the value from the comparison"""
        left, op, right = self.data
        left = try_render(left, local_envs, global_envs)
        right = try_render(right, local_envs, global_envs)
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
        raise SyntaxError(f'Unknown operator: {op}')

class TagFragGetItem(TagFrag):
    """Fragment for `obj[subscript]`"""

    def render(self, local_envs, global_envs):
        """Try to get the value of the getitem operation"""
        obj, subscript = self.data
        obj = try_render(obj, local_envs, global_envs)
        subscript = try_render(subscript, local_envs, global_envs)

        try:
            return obj[subscript]
        except KeyError:
            return EmptyDrop()

class TagFragGetAttr(TagFrag):
    """Fragment for `obj.attr`"""

    def render(self, local_envs, global_envs):
        """Try to get the value of the getattr operation"""
        obj, attr = self.data
        obj = try_render(obj, local_envs, global_envs)
        attr = str(attr)

        try:
            return getattr(obj, attr)
        except AttributeError as attr_ex:
            # support size query in liquid
            if attr == 'size':
                return len(obj)
            if attr == 'first':
                return obj[0]
            if attr == 'last':
                return obj[-1]
            return obj[attr]

class TagFragRange(TagFrag):
    """Fragment for range"""
    def render(self, local_envs, global_envs):
        start, end = self.data
        start = try_render(start, local_envs, global_envs)
        end = try_render(end, local_envs, global_envs)

        return list(range(int(start), int(end) + 1))

class TagFragFilter(TagFrag):
    """Filtername"""
    def render(self, local_envs, global_envs):
        filtername = str(self.data)
        try:
            return global_envs[LIQUID_FILTERS_ENVNAME][filtername]
        except KeyError:
            raise KeyError(f'No such filter: {filtername}') from None

class TagFragOutput(TagFrag):
    """Output inside {{ ... }}"""
    def render(self, local_envs, global_envs):
        base, filters = self.data
        base = try_render(base, local_envs, global_envs)
        for filt, fargs in filters:
            filt = filt.render(local_envs, global_envs)
            fargs = [try_render(farg, local_envs, global_envs)
                     for farg in fargs]
            fargs.insert(0, base)
            base = filt(*fargs)
        return base

def try_render(tagfrag, local_envs, global_envs):
    if isinstance(tagfrag, TagFrag):
        return tagfrag.render(local_envs, global_envs)
    return tagfrag
