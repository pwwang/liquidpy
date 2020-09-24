"""Exceptions for liquidpy, all based on `LiquidException`"""

class LiquidException(Exception):
    """The base class for all liquidpy exceptions"""

class LiquidNameError(LiquidException):
    """When wrong name or preserved keyword passed"""

class LiquidFilterRegistryException(LiquidException):
    """Raises when operate the filter registry incorrectly"""

class LiquidTagRegistryException(LiquidException):
    """Raises when operate the tag registry incorrectly"""

class LiquidSyntaxError(LiquidException):
    """Template syntax error

    Args:
        msg: The message for the exception
        context: The context
        parser: The parser
    """
    def __init__(self, msg, context=None, parser=None):
        # type: (str, Diot, Parser) -> None
        from .utils import excmsg_with_context
        super().__init__(excmsg_with_context(msg, context, parser))

class LiquidRenderError(LiquidException):
    """Template render error

    Args:
        msg: The message for the exception
        context: The context
        parser: The parser
    """
    def __init__(self, msg, context=None, parser=None):
        # type: (str, Diot, Parser) -> None
        from .utils import excmsg_with_context
        super().__init__(excmsg_with_context(msg, context, parser))
