"""The configuration for liquidpy"""
import logging
from diot import Diot
from .exceptions import LiquidConfigError

# some constants
LIQUID_LOGGER_NAME = 'LIQUID'
# Indentions to show the tree structure in logging
LIQUID_LOG_INDENT = '  '
LIQUID_FILTERS_ENVNAME = '__LIQUID_FILTERS__'

DEFAULT_CONFIG = Diot(
    extended=False,
    strict=True,
    debug=True
)

class Config(Diot):
    """The configurations for liquidpy"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set the default if not set
        for key in DEFAULT_CONFIG:
            if key not in self:
                self[key] = DEFAULT_CONFIG[key]

    def update_logger(self, from_template=False):
        """Update the logger configuration according to the configuration"""
        if self.strict and from_template:
            raise LiquidConfigError(
                'Not allowed to update logger in strict mode from template.'
            )
        if not self.logger:
            raise LiquidConfigError('Not logger initialized.')

        if not self.debug:
            self.logger.setLevel(logging.CRITICAL)
        elif self.debug is True:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                "[%(asctime)s][%(levelname)5s] %(name)s: %(message)s",
                "%m-%d %H:%M:%S"
            ))
            self.logger.addHandler(stream_handler)
