"""The configuration for liquidpy"""
from diot import Diot

DEFAULT_CONFIG = Diot(
    extended=False,
    strict=True
)

class Config(Diot):
    """The configurations for liquidpy"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set the default if not set
        for key in DEFAULT_CONFIG:
            if key not in self:
                self[key] = DEFAULT_CONFIG[key]
