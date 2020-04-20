"""Configurations for a Liquid object"""
import logging
from pathlib import Path
from contextlib import contextmanager
import attr
from attr_property import attr_property, attr_property_class
from .defaults import LIQUID_LOGGER_NAME

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def include_setter(this, value):
    """convert include relative paths to absolute paths"""
    # if include paths have already inferred
    if isinstance(value, list):
        return value
    if not isinstance(value, tuple):
        value = (value, "./")
    # save the raw values (converted after setter)
    # we want to keep previous directories
    raw = this.__attrs_property_raw__.get("include", [])
    subpaths = [Path(subpath.strip()) for subpath in value[0].split(';')]
    ret = []
    incdir = Path(value[1])
    if incdir.is_file():
        incdir = incdir.parent
    for subpath in subpaths:
        if subpath.is_absolute():
            ret.append(subpath)
        else:
            ret.append(incdir.resolve().joinpath(subpath))
    raw.extend(ret)
    return raw

def loglevel_setter(this, value): # pylint: disable=unused-argument
    """Convert and save loglevel, and change logger level"""
    if isinstance(value, str):
        value = value.upper()
        value = logging.getLevelName(value)
    LOGGER.setLevel(value)
    return value

def extends_setter(this, value):
    """convert include relative paths to absolute paths"""
    # save the raw values (converted after setter)
    # we want to keep previous directories
    if value is None:
        return []
    if isinstance(value, list):
        return value
    raw = this.__attrs_property_raw__.get("extends", [])
    subpaths = [Path(subpath.strip()) for subpath in value[0].split(';')]
    ret = []
    extdir = Path(value[1])
    if extdir.is_file():
        extdir = extdir.parent
    for subpath in subpaths:
        if subpath.is_absolute():
            ret.append(subpath)
        else:
            ret.append(extdir.resolve().joinpath(subpath))
    raw.extend(ret)
    return raw

# pylint: disable=too-few-public-methods
@attr_property_class
@attr.s(slots=True)
class LiquidConfig:

    """@API
    Configurations for a Liquid object

    @params:
        mode (str): The mode for `liquidpy` to handle the spaces
            arround open tags
        loglevel (int|str): The loglevel. Could be int identified
            by `logging` module or `detail/15` defined in `liquidpy`
        include (str): Paths to scan the included files
            - multiple paths separated by `;`
        extends (str): Paths to scan mother templates to extend.
            - multiple paths separated by `;`
    """
    # pylint: disable=no-self-use
    # the mode to parse the {%, {%- and alike
    # compact, loose
    mode = attr_property(validator_runtime=True,
                         deleter=False)
    loglevel = attr_property(setter=loglevel_setter,
                             deleter=False)
    include = attr_property(setter=include_setter,
                            deleter=False)
    extends = attr_property(setter=extends_setter,
                            deleter=False)

    @mode.validator
    def _model_validator(self, attribute, value):
        if value not in ("compact", "loose"):
            raise ValueError(f"Unknown model {value!r}, "
                             "expect 'compact' or 'loose'")

    @contextmanager
    def tear(self):
        """@API
        Leave a copy of config, when return,
        get the loglevel of LOGGER back
        @yields:
            (LiquidConfig): The new config object
        """
        config = LiquidConfig(
            mode=self.mode,
            loglevel=self.loglevel,
            include=self.include[:], # pylint: disable=unsubscriptable-object
            extends=self.extends[:] # pylint: disable=unsubscriptable-object
        )
        yield config

        if self.loglevel != config.loglevel:
            # trigger back the loglevel
            self.loglevel = self.loglevel
