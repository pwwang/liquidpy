"""The main class file for Liquid"""
import logging
from pathlib import Path
from .config import Config, LIQUID_LOGGER_NAME, LIQUID_FILTERS_ENVNAME
from .filtermgr import LIQUID_FILTERS

# For global LOGGER configurations
# Because all loggers are sub-loggers of this one
LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def _template_meta(template):
    if Path(template).is_file():
        template = Path(template)
        return template.stem, template.read_text()

    template_name = '<unknown>'
    template_content = ''

    if hasattr(template, 'name'):
        template_name = template.name
    if hasattr(template, 'read'):
        template_content = template.read()
    if isinstance(template, str):
        template_name = '<string>'
        template_content = template
    return template_name, template_content

class Liquid:
    """Liquid class"""
    LOGGER_NAMES = {}

    def __init__(self, liquid_template, liquid_config=None, **envs):
        self.envs = envs
        self.config = Config(liquid_config or {})
        if self.config.extended:
            from .extended.parser import ExtendedParser as Parser
        else:
            from .standard.parser import StandardParser as Parser

        # // TODO Cache parsed object
        template_name, template_content = _template_meta(liquid_template)

        logger_name = self._logger_name(template_name)
        self.config.logger = logging.getLogger(logger_name)
        # update the logger configuration
        self.config.update_logger()

        self.parsed = Parser(self.config).parse(
            template_content, template_name
        )

    def render(self, **context):
        """Render the template with given context

        The parsed is a TagRoot object, whose render gives a string
        """
        envs = self.envs.copy()
        envs.update(context)
        # not expecting users to break the filters __LIQUID_FILTERS__
        # // TODO: raise errors if user specified this key?
        envs[LIQUID_FILTERS_ENVNAME] = LIQUID_FILTERS
        return self.parsed.render(envs, envs)[0]

    def _logger_name(self, template_name):
        if Path(template_name).exists():
            template_name = Path(template_name).stem

        name_count = list(Liquid.LOGGER_NAMES.values()).count(template_name)
        suffix = '' if name_count == 0 else f'_{name_count}'
        Liquid.LOGGER_NAMES[id(self)] = template_name

        return f"{LIQUID_LOGGER_NAME}.{template_name}{suffix}"
