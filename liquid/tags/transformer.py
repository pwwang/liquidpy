"""The transformer for tag segments"""
import ast
from abc import ABC, abstractmethod
from functools import partialmethod
from collections import OrderedDict
from lark import v_args, Transformer
from ..config import LIQUID_FILTERS_ENVNAME
from ..filters import EmptyDrop
from ..utils import NOTHING
from ..exceptions import LiquidNameError

def render_segment(tagseg, local_vars, global_vars):
    # type: (dict, dict) -> Any
    """Try to render a segment

    If it is a tagseg object, render it with the envs,
    otherwise, return the value itself

    Args:
        local_vars: The local variables
        global_vars: The global_vars

    Returns:
        The rendered value
    """
    if isinstance(tagseg, TagSegment):
        return tagseg.render(local_vars, global_vars)
    return tagseg

class TagSegment(ABC):
    """Base class for segment classes

    The parsed objects for the syntax inside a tag

    Attributes:
        data: The data to parser
    """
    __slots__ = ('_data', )

    def __init__(self, *data):
        # type: (*Any)
        """Initialize the object
        Args:
            data: The data of the parsed object
        """
        self._data = data

    @property
    def data(self):
        """Get the data"""
        return self._data

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f'<{self.__class__.__name__}(data={self.data!r})>'

    @abstractmethod
    def render(self, local_vars, global_vars):
        # type: (dict, dict) -> Any
        # pylint: disable=unused-argument
        """Render the segment with the given envs"""

class TagSegmentVar(TagSegment):
    """segment for variables"""
    __slots__ = ('_data', 'line', 'column')

    def __init__(self, *data):
        # type: (Any) -> None
        """Initialize the object
        Args:
            data: The data of the parsed object
        """
        super().__init__(*data)
        try:
            self.line = data[0].line
            self.column = data[0].column
        except AttributeError:
            pass

    def __str__(self):
        return str(self.data[0])

    def render(self, local_vars, global_vars):
        """Get the value of a variable from envs"""
        vname_token = self.data[0]
        varname = str(vname_token)
        if varname in local_vars:
            var = local_vars[varname]
        else:
            try:
                var = global_vars[varname]
            except KeyError:
                error = LiquidNameError(
                    f'Variable not defined: {varname!r}.'
                )
                error.lineno = vname_token.line
                error.colno = vname_token.column
                raise error from None
        if isinstance(var, (tuple, list)) and len(var) == 0:
            return EmptyDrop()
        return var

class TagSegmentComparison(TagSegment):
    """Comparison segment"""
    def render(self, local_vars, global_vars):
        """Render the segment"""
        # pylint: disable=too-many-return-statements
        left, op, right = self.data
        left = render_segment(left, local_vars, global_vars)
        right = render_segment(right, local_vars, global_vars)
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "==":
            return left == right
        if op == ">=":
            return left >= right
        if op == "<=":
            return left <= right
        if op in ("<>", "!="):
            return left != right
        if op == "in":
            return left in right
        if op == "notin":
            return left not in right
        if op == "is":
            return left is right
        if op == "isnot":
            return left is not right
        if op == "contains":
            return right in left
        return None # pragma: no cover

class TagSegmentGetItem(TagSegment):
    """segment for `obj[subscript]`"""

    def render(self, local_vars, global_vars):
        """Try to get the value of the getitem operation"""
        obj, subscript = self.data
        obj = render_segment(obj, local_vars, global_vars)
        subscript = render_segment(subscript, local_vars, global_vars)

        try:
            return obj[subscript]
        except KeyError:
            return EmptyDrop()

class TagSegmentGetAttr(TagSegment):
    """segment for `obj.attr`"""

    def render(self, local_vars, global_vars):
        """Try to get the value of the getattr operation"""
        obj, attr = self.data
        obj = render_segment(obj, local_vars, global_vars)
        attr = str(attr)

        try:
            return getattr(obj, attr)
        except AttributeError as attre:
            # support size query in liquid
            try:
                if attr == 'size':
                    return len(obj)
                if attr == 'first':
                    return obj[0]
                if attr == 'last':
                    return obj[-1]
                return obj[attr]
            except (KeyError, TypeError):
                raise attre from None

class TagSegmentRange(TagSegment):
    """segment for range"""
    def render(self, local_vars, global_vars):
        """Render the range segment"""
        start, end = self.data
        start = render_segment(start, local_vars, global_vars)
        end = render_segment(end, local_vars, global_vars)

        return list(range(int(start), int(end) + 1))

class TagSegmentOutput(TagSegment):
    """Output inside {{ ... }}"""
    def render(self, local_vars, global_vars):
        """Render the output segment"""
        base = render_segment(self.data[0], local_vars, global_vars)
        if len(self) == 1:
            return base

        # filter_name is Token
        for filter_func in self.data[1:]:
            base = filter_func.render(local_vars, global_vars)(base)

        return base

class TagSegmentArguments(TagSegment):
    """Arguments segment"""
    # pylint: disable=arguments-differ
    def render(self, local_vars, global_vars, as_is=False):
        # type: (dict, dict, bool) -> Tuple[List[str], Dict[str, Any]]
        """Render the segment

        Args:
            as_is: Whether render the non-keyword arguments as-is or treat
                them as variables

        Returns:
            Rendered non-keyword and keyword arguments
        """
        args = []
        kwargs = OrderedDict()
        for test1, test2 in self.data:
            test1name = str(test1)

            if test2 is NOTHING:
                args.append(test1name if as_is
                            else render_segment(test1, local_vars, global_vars))
            else:
                kwargs[test1name] = render_segment(
                    test2, local_vars, global_vars
                )
        return args, kwargs

class TagSegmentLogical(TagSegment):
    """Logical segment"""
    def render(self, local_vars, global_vars):
        test1, and_or, test2 = self.data
        test1 = render_segment(test1, local_vars, global_vars)
        test2 = render_segment(test2, local_vars, global_vars)
        if and_or == 'and':
            return test1 and test2
        return test1 or test2

class TagSegmentFilter(TagSegment):
    """Filter segment"""
    def render(self, local_vars, global_vars):
        filter_name, filter_args = self.data

        args, kwargs = [], {}
        if filter_args is not NOTHING:
            rendered_args = render_segment(filter_args, local_vars, global_vars)
            if rendered_args is not None:
                args, kwargs = rendered_args

        filtname = str(filter_name)

        filter_func_orig = global_vars[LIQUID_FILTERS_ENVNAME].get(
            filtname, global_vars.get(filtname, NOTHING)
        )

        if filter_func_orig is NOTHING:
            error = KeyError(f'No such filter: {filtname!r}')
            error.lineno = filter_name.line
            error.colno = filter_name.column
            raise error

        def filter_func(base):
            filter_args = [base] + args
            return filter_func_orig(*filter_args, **kwargs)

        return filter_func

@v_args(inline=True)
class TagTransformer(Transformer):
    """Transform tag segments"""
    # pylint: disable=no-self-use

    def __init__(self, visit_tokens=False):
        """Change visit_tokens default to False"""
        # pylint: disable=useless-super-delegation
        super().__init__(visit_tokens)

    def range(self, token):
        """Ranges"""
        start, stop = token[1:-1].split('..', 1)
        try:
            start = int(start)
        except (TypeError, ValueError):
            start = TagSegmentVar(start)
        try:
            stop = int(stop)
        except (TypeError, ValueError):
            stop = TagSegmentVar(stop)
        return TagSegmentRange(start, stop)

    def comparison(self, expr, op=None, expr2=None):
        """rule comparison: comparison: atom (_comp_op atom)?"""
        if op is None:
            return expr
        return TagSegmentComparison(expr, op, expr2)

    def varname(self, vname):
        """Keep the token information for tracking"""
        return vname

    def argvalue(self, test1, test2=NOTHING):
        """rule argvalue: test ("=" test)?"""
        return (test1, test2)

    def _passby(self, *args):
        return args

    def _passby_segment(self, *args, segment=None):
        return segment(*args)

    def _passby_single_segment(self, arg=NOTHING, segment=None):
        return segment(arg)

    number = string = lambda _, data: ast.literal_eval(str(data))
    get_item = partialmethod(_passby_segment, segment=TagSegmentGetItem)
    get_attr = partialmethod(_passby_segment, segment=TagSegmentGetAttr)
    arguments = partialmethod(_passby_segment, segment=TagSegmentArguments)
    var = partialmethod(_passby_segment, segment=TagSegmentVar)
    output = partialmethod(_passby_segment, segment=TagSegmentOutput)
    logical_test = partialmethod(_passby_segment, segment=TagSegmentLogical)
    test_filter = partialmethod(_passby_segment, segment=TagSegmentFilter)
    const_none = lambda _: None
    const_true = lambda _: True
    const_false = lambda _: False
