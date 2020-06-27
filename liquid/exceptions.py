"""Exceptions for liquidpy, all based on `LiquidException`"""

class LiquidException(Exception):
    """The base class for all liquidpy exceptions"""

class LiquidConfigError(LiquidException):
    """When something goes wrong with the configurations"""

class TagRegistryException(LiquidException):
    """Raises when operate the tag registry incorrectly"""

class FilterRegistryException(LiquidException):
    """Raises when operate the filter registry incorrectly"""

class LiquidSyntaxError(LiquidException):
    """Template syntax error"""

class LiquidRenderError(LiquidException):
    """Template render error"""

class TagRenderError(LiquidRenderError):
    """When failed to render tag fragments"""

class EndTagUnexpected(LiquidSyntaxError):
    """Raises when an end tag is unexpected (not matching the open one)"""

class TagUnclosed(LiquidSyntaxError):
    """Raises when a non-VOID tag left unclosed"""

class TagSyntaxError(LiquidSyntaxError):
    """Syntax error for a tag"""

class TagWrongPosition(LiquidSyntaxError):
    """Raises when a tag is in a wrong position"""
