"""Provides filter manager"""
from typing import TYPE_CHECKING, Callable, Dict, Sequence, Union

if TYPE_CHECKING:
    from jinja2 import Environment


class FilterManager:
    """A manager for filters

    Attributes:
        filters: a mapping of filter names to filters
    """

    __slots__ = ("filters",)

    def __init__(self) -> None:
        """Constructor"""
        self.filters: Dict[str, Callable] = {}

    def register(
        self, name_or_filter: Union[str, Sequence[str], Callable] = None
    ) -> Callable:
        """Register a filter

        This can be used as a decorator

        Examples:
            >>> @filter_manager.register
            >>> def add(a, b):
            >>>   return a+b
            >>> # register it with an alias:
            >>> @filter_manager.register('addfunc')
            >>> def add(a, b):
            >>>   return a+b

        Args:
            name_or_filter: The filter to register
                if name is given, will be treated as alias

        Returns:
            The registered function or the decorator
        """

        def decorator(filterfunc: Callable) -> Callable:
            name = filterfunc.__name__
            name = [name]  # type: ignore

            if name_or_filter and name_or_filter is not filterfunc:
                names = name_or_filter
                if isinstance(names, str):
                    names = (
                        nam.strip() for nam in names.split(",")
                    )  # type: ignore
                name = names  # type: ignore
            for nam in name:
                self.filters[nam] = filterfunc

            return filterfunc

        if callable(name_or_filter):
            return decorator(name_or_filter)

        return decorator

    def update_to_env(
        self, env: "Environment", overwrite: bool = True
    ) -> None:
        """Update the filters to environment

        Args:
            env: The environment to update these filters to
            overwrite: Whether overwrite existing filters in the env?
        """
        if overwrite:
            env.filters.update(self.filters)

        filters = self.filters.copy()
        filters.update(env.filters)
        env.filters = filters
