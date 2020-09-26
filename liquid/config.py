"""The configuration for liquidpy

Attributes:
    LIQUID_LOGGER_NAME: The name of the logger
    LIQUID_LOG_INDENT: Indentions to show the tree structure in logging
    LIQUID_FILTERS_ENVNAME: The variable containing all filters
    LIQUID_EXC_MAX_STACKS: The stacks to show in exceptions when debug is on
    LIQUID_EXC_CODE_CONTEXT: The number of context lines to show codes in
        exceptions when debug is on
    DEFAULT_CONFIG: The default configuration
"""
import logging
from diot import Diot

# some constants

LIQUID_LOGGER_NAME = 'LIQUID'                  # type: str
LIQUID_LOG_INDENT = '  '                       # type: str
LIQUID_FILTERS_ENVNAME = '__LIQUID_FILTERS__'  # type: str
LIQUID_EXC_MAX_STACKS = 5                      # type: int
LIQUID_EXC_CODE_CONTEXT = 3                    # type: int

DEFAULT_CONFIG = Diot(
    mode='standard',
    strict=True,
    debug=False,
    cache=False,
    extends_dir=[],
    include_dir=[]
) # type: Diot

class Config(Diot):
    """The configurations for liquidpy"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the default if not set
        self |= DEFAULT_CONFIG | self

    def update_logger(self):
        # type: (bool) -> None
        """Update the logger configuration according to the configuration
        """

        from .utils import logger

        if not self.debug:
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.DEBUG)
