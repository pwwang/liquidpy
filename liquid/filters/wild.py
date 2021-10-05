"""Provides some wild filters"""

try:
    from jinja2 import pass_environment
except ImportError:
    from jinja2 import environmentfilter as pass_environment

from typing import TYPE_CHECKING, Any
from .manager import FilterManager

if TYPE_CHECKING:
    from jinja2.environment import Environment

wild_filter_manager = FilterManager()


@wild_filter_manager.register("ifelse, if_else")
@pass_environment
def ifelse(
    env: "Environment",
    value: Any,
    test: Any,
    test_args: Any = (),
    true: Any = None,
    true_args: Any = (),
    false: Any = None,
    false_args: Any = (),
) -> Any:
    """An if-else filter, implementing a tenary-like filter.

    Use `ifelse` or `if_else`.

    Examples:
        >>> {{ a | ifelse: isinstance, (int, ),
        >>>                "plus", (1, ),
        >>>                "append", (".html", ) }}
        >>> # 2 when a = 1
        >>> # "a.html" when a = "a"

    Args:
        value: The base value
        test: The test callable or filter name
        test_args: Other args (value as the first arg) for the test
        true: The callable or filter name when test is True
        true_args: Other args (value as the first arg) for the true
            When this is None, return the true callable itself or the name
            of the filter it self
        false: The callable or filter name when test is False
        false_args: Other args (value as the first arg) for the false
            When this is None, return the false callable itself or the name
            of the filter it self
    Returns:
        The result of true of test result is True otherwise result of false.
    """

    def compile_out(func: Any, args: Any) -> Any:
        if args is None:
            return func
        if not isinstance(args, tuple):
            args = (args,)
        if callable(func):
            return func(value, *args)
        expr = env.compile_expression(f"value | {func}(*args)")
        return expr(value=value, args=args)

    test_out = compile_out(test, test_args)
    if test_out:
        return compile_out(true, true_args)
    return compile_out(false, false_args)
