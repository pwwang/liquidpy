"""The main class file for Liquid"""
from .config import Config

class Liquid:
    """Liquid class"""

    def __init__(self, liquid_template, liquid_config=None, **envs):
        self.envs = envs
        self.config = Config(liquid_config or {})

        if self.config.extended:
            from .extended import parser
        else:
            from .standard import parser

        # // TODO Allowing file-like object/stream and file
        # // TODO Cache parsed object
        self.parsed = parser.parse(liquid_template)

    def render(self, **context):
        """Render the template with given context

        The parsed is a TagRoot object, whose render gives a string
        """
        envs = self.envs.copy()
        envs.update(context)
        return self.parsed.render(envs)[0]
