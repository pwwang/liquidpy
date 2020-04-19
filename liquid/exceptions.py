"""
Exceptions used in liquidpy
"""
import logging
from .defaults import LIQUID_LOGGER_NAME, LIQUID_LOGLEVELID_DETAIL
LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

class LiquidSyntaxError(Exception):
    """Raises when there is a syntax error in the template"""

    def __init__(self, message, context=None):
        """
        Initialize the exception
        @params:
            message (str): The error message
            parser (LiquidParser): The parser
        """
        if not context or LOGGER.level >= LIQUID_LOGLEVELID_DETAIL:
            # just pop the message
            pass
        elif context and context.parser:
            # if we have the context and we are at a higher log level
            message = [message, '']
            message.append('Template call stacks:')
            message.append('----------------------------------------------')
            message.extend(context.parser.call_stacks())
            message = "\n".join(message)
        else:
            # we don't have parser, but we may have filename and lineno
            message = f"{context.filename}:{context.lineno}\n{message}"

        super().__init__(message)

class LiquidRenderError(Exception):
    """Raises when the template fails to render"""

class LiquidCodeTagExists(Exception):
    """Raises when codes with tag has already been added"""

class LiquidExpressionFilterModifierException(Exception):
    """When incompatible modifiers are assigned to a filter"""

class LiquidNodeAlreadyRegistered(Exception):
    """When a node is already registered"""

class LiquidNameError(Exception):
    """When an invalid variable name used"""
