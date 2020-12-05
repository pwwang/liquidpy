"""Provides Liquid, LiquidPython and LiquidJekyll classes"""
from .config import Config, LIQUID_FILTERS_ENVNAME
from .utils import template_meta, check_name
from .parser import Parser
from .filters import filter_manager, EmptyDrop
# from .jekyll.parser import Parser as ParserJekyll
# from .jekyll.filters import filter_manager as filter_manager_jekyll
from .python.parser import Parser as ParserPython
from .python.filters import filter_manager as filter_manager_python

class Liquid:
    """The main class for external use

    One could provide a config says `liquid_config['extended'] = True` to
    switch this object to be initialized as a LiquidPython object.

    Examples:
        >>> liq1 = Liquid("{{a}}")
        >>> liq1.__class__ # -> Liquid
        >>> liq2 = Liquid("{{a}}", {'mode': 'python'})
        >>> liq2.__class__ # -> LiquidPython
        >>> isinstance(liq2, Liquid) # -> True

    Attributes:
        PARSER_CLASS: The root parser class
        FILTER_MANAGER: The filter manager

    Args:
        liquid_template: The template that can be rendered.
            It could be a string template, a path to a file contains the
            template or an IO object with the template
        liquid_config: The configuration for this liquid object
            - extended: Whether use the extended mode
            -
        **envs: Other environment variables for template rendering.
    """
    PARSER_CLASS = Parser
    FILTER_MANAGER = filter_manager

    # pylint: disable=unused-argument
    def __new__(cls, liquid_template, liquid_config=None, **envs):
        # type: (Union[str, Path, IO], Optional[Dict[str, Any]], Any) -> Liquid
        """Works as a router to determine returning a Liquid or LiquidPython
        object according to liquid_config['extended']
        """

        mode = (liquid_config.get('mode')
                if liquid_config
                else None) # type: str
        # if mode == 'jekyll':
        #     return LiquidJekyll.__new__(LiquidJekyll)
        if mode == 'python':
            return LiquidPython.__new__(LiquidPython)
        return super().__new__(cls)
    # pylint: enable=unused-argument

    def __init__(self, liquid_template, liquid_config=None, **envs):
        # type: (Union[str, Path, IO], Optional[Dict[str, Any]], Any) -> None
        # since __new__ returns an object anyway is a Liquid object
        # we will need to pass handling to LiquidPython itself

        check_name(envs)
        self.envs = envs
        self.config = Config(liquid_config or {})
        self.config.update_logger()
        self.meta = template_meta(liquid_template)
        self.parsed = self._from_cache(liquid_template)

    # pylint: disable=unused-argument
    def _from_cache(self, liquid_template):
        #  (Union[str, Path, IO]) -> Type[Parser]
        """Try to the parsed object from the cache

        // Todo: When config.cache is False, don't cache
        When True, try to cache it in memory, otherwise a directory should
        be specified, objects are cached there
        """
        parsed = self.PARSER_CLASS(self.meta, self.config).parse()
        return parsed
    # pylint: enable=unused-argument

    def __del__(self):
        try:
            if self.meta.should_close:
                self.meta.stream.close()
        except AttributeError: # pragma: no cover
            pass

    def _update_context(self, context):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """Update the given context based on pre-set envs"""
        check_name(context)
        envs = self.envs.copy() # type: Dict[str, Any]
        envs.update(context)
        return envs

    def _render(self, local_vars: dict, global_vars: dict) -> str:
        # render and return
        try:
            return self.parsed.render(local_vars, global_vars)[0]
        finally:
            # debug mode needs stream to print stack details
            if self.meta.should_close:
                self.meta.stream.close()

    def render(self, **context):
        # type: (Any) -> str
        """Render the template with given context
        The parsed is a TagRoot object, whose render gives a string

        Args:
            context: The context used to render the template

        Returns:
            The rendered content
        """
        context = self._update_context(context)
        global_context = context.copy()
        global_context[
            LIQUID_FILTERS_ENVNAME
        ] = self.FILTER_MANAGER.filters
        # liquid's EmptyDrop object
        global_context['empty'] = EmptyDrop()
        return self._render(context, global_context)

# class LiquidJekyll(Liquid):
#     """Support for extended mode of liquidpy"""
#     PARSER_CLASS = ParserJekyll
#     FILTER_MANAGER = filter_manager_jekyll

#     __new__ = object.__new__

#     def __init__(self, liquid_template, liquid_config=None, **envs):
#         # type: (Union[str, Path, IO], Optional[Dict[str, Any]], Any) -> None
#         # pylint: disable=super-init-not-called
#         self._init(liquid_template, liquid_config, **envs)

class LiquidPython(Liquid):
    # pylint: disable=too-few-public-methods
    """Support for extended mode of liquidpy"""
    PARSER_CLASS = ParserPython
    FILTER_MANAGER = filter_manager_python

    # pylint: disable=signature-differs,unused-argument,arguments-differ
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def render(self, **context):
        # type: (Any) -> str
        """Render the template with given context
        The parsed is a TagRoot object, whose render gives a string

        Args:
            context: The context used to render the template

        Returns:
            The rendered content
        """
        context = self._update_context(context)
        global_context = __builtins__.copy()
        global_context.update(context)

        global_context[
            LIQUID_FILTERS_ENVNAME
        ] = self.FILTER_MANAGER.filters
        return self._render(context, global_context)
