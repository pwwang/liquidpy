"""Provides Liquid class"""
import builtins
from typing import Any, Callable, Mapping
from jinja2 import (
    Environment,
    ChoiceLoader,
    FileSystemLoader,
)

from .filters.standard import standard_filter_manager
from .utils import PathType, PathTypeOrIter


class Liquid:
    """The entrance for the package

    Examples:
        >>> Liquid('{{a}}', from_file=False)
        >>> Liquid('template.html')

    Args:
        template: The template string or path of the template file
        env: The jinja environment
        from_file: Whether `template` is a file path. If True, a
            `FileSystemLoader` will be used in the `env`.
        mode: The mode of the engine.
            - standard: Most compatibility with the standard liquid engine
            - jekyll: The jekyll-compatible mode
            - shopify: The shopify-compatible mode
            - wild: The liquid- and jinja-compatible mode
        filter_with_colon: Whether enable to use colon to separate filter and
            its arguments (i.e. `{{a | filter: arg}}`). If False, will
            fallback to use parentheses (`{{a | filter(arg)}}`)
        search_paths: The search paths for the template files.
            This only supports specification of paths. If you need so specify
            `encoding` and/or `followlinks`, you should use jinja's
            `FileSystemLoader`
        globals: Additional global values to be used to render the template
        filters: Additional filters be to used to render the template
        filters_as_globals: Whether also use filters as globals
            Only works in wild mode
        **kwargs: Other arguments for an jinja Environment construction and
            configurations for extensions
    """

    __slots__ = ("env", "template")

    def __init__(
        self,
        template: PathType,
        from_file: bool = None,
        mode: str = None,
        env: Environment = None,
        filter_with_colon: bool = None,
        search_paths: PathTypeOrIter = None,
        globals: Mapping[str, Any] = None,
        filters: Mapping[str, Callable] = None,
        filters_as_globals: bool = None,
        **kwargs: Any,
    ) -> None:
        """Constructor"""
        # default values
        # fetch at runtime, so that they can be configured at importing
        from .defaults import (
            FROM_FILE,
            MODE,
            FILTER_WITH_COLON,
            SEARCH_PATHS,
            ENV_ARGS,
            SHARED_GLOBALS,
            FILTERS_AS_GLOBALS,
        )

        if from_file is None:
            from_file = FROM_FILE
        if mode is None:
            mode = MODE
        if filter_with_colon is None:
            filter_with_colon = FILTER_WITH_COLON
        if search_paths is None:
            search_paths = SEARCH_PATHS
        if filters_as_globals is None:
            filters_as_globals = FILTERS_AS_GLOBALS

        # split kwargs into arguments for Environment constructor and
        # configurations for extensions
        env_args = {}
        ext_conf = {}
        for key, val in kwargs.items():
            if key in ENV_ARGS:
                env_args[key] = val
            else:
                ext_conf[key] = val

        loader = env_args.pop("loader", None)
        fsloader = FileSystemLoader(search_paths)  # type: ignore
        if loader:
            loader = ChoiceLoader([loader, fsloader])
        else:
            loader = fsloader

        self.env = env = Environment(**env_args, loader=loader)
        env.extend(**ext_conf)
        env.globals.update(SHARED_GLOBALS)

        standard_filter_manager.update_to_env(env)
        env.add_extension("jinja2.ext.loopcontrols")
        if filter_with_colon:
            from .exts.filter_colon import FilterColonExtension

            env.add_extension(FilterColonExtension)

        if mode == "wild":
            from .exts.wild import LiquidWildExtension
            from .filters.wild import wild_filter_manager

            env.add_extension("jinja2.ext.debug")
            env.add_extension(LiquidWildExtension)

            bfilters = {
                key: getattr(builtins, key)
                for key in dir(builtins)
                if not key.startswith("_")
                and callable(getattr(builtins, key))
                and key
                not in (
                    "copyright",
                    "credits",
                    "input",
                    "help",
                    "globals",
                    "license",
                    "locals",
                    "memoryview",
                    "object",
                    "property",
                    "staticmethod",
                    "super",
                )
                and not any(key_c.isupper() for key_c in key)
            }
            env.filters.update(bfilters)
            wild_filter_manager.update_to_env(env)
            env.globals.update(
                {
                    key: val
                    for key, val in __builtins__.items()
                    if not key.startswith("_")
                }
            )
            if filters_as_globals:
                env.globals.update(standard_filter_manager.filters)
                env.globals.update(wild_filter_manager.filters)

        elif mode == "jekyll":
            from .exts.front_matter import FrontMatterExtension
            from .exts.jekyll import LiquidJekyllExtension
            from .filters.jekyll import jekyll_filter_manager

            jekyll_filter_manager.update_to_env(env)
            env.add_extension(FrontMatterExtension)
            env.add_extension(LiquidJekyllExtension)

        elif mode == "shopify":
            from .exts.shopify import LiquidShopifyExtension
            from .filters.shopify import shopify_filter_manager

            shopify_filter_manager.update_to_env(env)
            env.add_extension(LiquidShopifyExtension)

        else:  # standard
            from .exts.standard import LiquidStandardExtension

            env.add_extension(LiquidStandardExtension)

        if filters:
            env.filters.update(filters)

        builtin_globals = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool
        }
        if globals:
            builtin_globals.update(globals)
        env.globals.update(builtin_globals)

        if from_file:
            # in case template is a PathLike
            self.template = env.get_template(str(template))
        else:
            self.template = env.from_string(str(template))

    def render(self, *args, **kwargs) -> Any:
        """Render the template.

        You can either pass the values using `tpl.render(a=1)` or
        `tpl.render({'a': 1})`
        """
        return self.template.render(*args, **kwargs)

    async def render_async(self, *args, **kwargs) -> Any:
        """Asynchronously render the template"""
        return await self.template.render_async(*args, **kwargs)

    @classmethod
    def from_env(
        cls,
        template: PathType,
        env: Environment,
        from_file: bool = None,
        filter_with_colon: bool = None,
        filters_as_globals: bool = None,
        mode: str = None,
    ) -> "Liquid":
        """Initiate a template from a jinja environment

        You should not specify any liquid-related extensions here. They will
        be added automatically.

        No search path is allow to be passed here. Instead, use jinja2's
        loaders or use the constructor to initialize a template.

        @Args:
            template: The template string or path of the template file
            env: The jinja environment
            from_file: Whether `template` is a file path. If True, a
                `FileSystemLoader` will be used in the `env`.
            filter_with_colon: Whether enable to use colon to separate filter
                and its arguments (i.e. `{{a | filter: arg}}`). If False, will
                fallback to use parentheses (`{{a | filter(arg)}}`)
            filters_as_globals: Whether also use filters as globals
                Only works in wild mode
            mode: The mode of the engine.
                - standard: Most compatibility with the standard liquid engine
                - wild: The liquid- and jinja-compatible mode
                - jekyll: The jekyll-compatible mode

        @Returns:
            A `Liquid` object
        """
        return cls(
            template,
            env=env,
            from_file=from_file,
            filter_with_colon=filter_with_colon,
            filters_as_globals=filters_as_globals,
            mode=mode,
        )
