"""
Liquid template engine for python
"""
__version__ = "0.5.0"
import sys
import traceback
import logging
import warnings
import keyword
from .stream import LiquidStream
from .parser import LiquidParser
from .exceptions import (
    LiquidSyntaxError,
    LiquidRenderError,
    LiquidNameError,
)
from .filters import LIQUID_FILTERS, PYTHON_FILTERS
from .code import LiquidCode
from .config import LiquidConfig
from .defaults import (
    LIQUID_LOGGER_NAME,
    LIQUID_DEFAULT_MODE,
    LIQUID_DEFAULT_ENVS,
    LIQUID_COMPILED_SOURCE_NAME,
    LIQUID_LIQUID_FILTERS,
    LIQUID_TEXT_FILENAME,
    LIQUID_STREAM_FILENAME,
    LIQUID_LOGLEVELID_DETAIL,
)

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def _shorten(string, length=15):
    """Shorten a string used in debug information"""
    string = repr(string)[1:-1]
    if len(string) < length:
        return string
    remain = int(len(string) / 2 - 5)
    return f"{string[:remain]} ... {string[-remain:]}"

def _check_vars(envs):
    """Check if variable names are valid"""
    for varname in envs:
        if not varname.isidentifier() or varname in keyword.kwlist:
            raise LiquidNameError(f"Invalid variable name: {varname!r}")

def _render_failed(exc, finalcode, final_context):
    """Format the message with more details when rendering failed"""
    source_line = None
    source_lineno = None
    # we start from the lastest trackback
    for tback in reversed(traceback.extract_tb(sys.exc_info()[2])):
        # we expect the exception from our compile source
        if tback.filename != LIQUID_COMPILED_SOURCE_NAME: # pragma: no cover
            continue
        source_lineno = tback.lineno
        source_line = finalcode.get_line(source_lineno - 1)
        if source_line.context:
            break

    msg = [f"[{type(exc).__name__}] {exc!s}"]
    if LOGGER.level > LIQUID_LOGLEVELID_DETAIL:
        # exception is not from our compile source
        # or loglevel is higher than DETAIL
        raise LiquidRenderError(msg[0]) from None

    if source_line and source_line.context:
        msg.append('')
        msg.append("Template call stacks:")
        msg.append('-' * 50)
        msg.extend(source_line.context.parser.call_stacks(
            source_line.lineno
        ))

    # Only show compiled source if we are at debug level
    if LOGGER.level > 10:
        raise LiquidRenderError('\n'.join(msg)) from None

    # it could be IndentationError, which filename and lineno will not be
    # revealed in trackbacks, we need to parse it from exception message
    if (source_lineno is None and
            f"({LIQUID_COMPILED_SOURCE_NAME}, line " in msg[0]):
        # try to get line number from '(<LIQUID_COMPILED_SOURCE>, line 40)'
        maybe_lineno = (msg[0]
                        .split(f"({LIQUID_COMPILED_SOURCE_NAME}, line ")[1]
                        .split(')')[0])
        if maybe_lineno.isdigit():
            source_lineno = int(maybe_lineno)

    if source_lineno is not None:
        msg.append('')
        msg.append("Compiled source (elevate loglevel to hide this)")
        msg.append('-' * 50)
        msg.extend(LiquidStream.from_string(str(finalcode)).
                   get_context(source_lineno))

    # attach context as well
    msg.append('')
    msg.append("Context:")
    msg.append('-' * 50)
    for key, val in final_context.items():
        if key == LIQUID_LIQUID_FILTERS:
            continue
        if isinstance(val, dict):
            msg.append(f'  {key}:')
            msg.extend(f'     {k}: {_shorten(str(v), 80)}'
                       for k, v in val.items())
        elif isinstance(val, (list, tuple, set)):
            msg.append(f'  {key}:')
            msg.extend(f'   - {_shorten(str(v), 80)}' for v in val)
        else:
            msg.append(f'  {key}: {_shorten(str(val), 80)}')

    raise LiquidRenderError('\n'.join(msg)) from None

class Liquid:

    """@API
    The main entrance class for `liquidpy` to initiate a template
    """

    @staticmethod
    def debug(dbg=None): # pylint: disable=unused-argument
        """
        Set or get the debug mode
        @params:
            dbg: `None` to return if now we are in debug mode
                - True/False to turn on/off the debug mode
        @returns:
            Return the current debug mode when `dbg` is `None`
        """
        warnings.warn("Liquid.debug is deprecated and takes no effect "
                      "anymore, use argument liquid_loglevel of "
                      "Liquid constructor instead.",
                      DeprecationWarning)

    def __init__(self, # pylint: disable=too-many-arguments
                 liquid_template='',
                 from_file=None,
                 liquid_loglevel=LIQUID_LOGLEVELID_DETAIL,
                 liquid_include="./",
                 liquid_extends=None,
                 liquid_mode=LIQUID_DEFAULT_MODE,
                 liquid_from_file=False,
                 liquid_from_stream=False,
                 **envs):
        """API
        Initialize a liquid object
        @params:
            liquid_template (str|stream): The template string/file/stream
            from_file (str): `Deprecated!` Use `liquid_template` and
                `liquid_from_file=True` instead.
            liquid_loglevel (int|str): The loglevel. Could be int identified
                by `logging` module or `detail/15` defined in `liquidpy`
            liquid_include (str): Paths to scan the included files
                - multiple paths separated by `;`
            liquid_extends (str): Paths to scan mother templates to extend.
                - multiple paths separated by `;`
            liquid_mode (str): The mode for `liquidpy` to handle spaces
                arround open tags
            liquid_from_file (bool): Indicating whether `liquid_template` is
                a file path
            liquid_from_stream (bool): Indicating whether `liquid_template` is
                a stream
            **envs: The environment.
        """
        _check_vars(envs)

        if from_file:
            warnings.warn("Argument 'from_file' is deprecated, use "
                          "'liquid_template=<file>, liquid_from_file=True' "
                          "instead.", DeprecationWarning)
            liquid_template = from_file
            liquid_from_file = True

        if liquid_from_stream:
            self.filename = LIQUID_STREAM_FILENAME
            self.stream = LiquidStream.from_stream(liquid_template)
        elif liquid_from_file:
            self.filename = liquid_template
            self.stream = LiquidStream.from_file(liquid_template)
        else:
            self.filename = LIQUID_TEXT_FILENAME
            self.stream = LiquidStream.from_string(liquid_template)

        self.envs = LIQUID_DEFAULT_ENVS.copy()
        self.envs.update(envs)
        self.envs.update(PYTHON_FILTERS)
        self.envs[LIQUID_LIQUID_FILTERS] = LIQUID_FILTERS

        config = LiquidConfig(mode=liquid_mode,
                              include=(liquid_include, './'),
                              extends=liquid_extends and (liquid_extends, './'),
                              loglevel=liquid_loglevel)
        self.parser = LiquidParser(filename=self.filename,
                                   # this is gonna be added to
                                   # the render function
                                   shared_code=LiquidCode(indent=1),
                                   code=LiquidCode(indent=1),
                                   prev=None,
                                   config=config,
                                   stream=self.stream)

        self.parser.parse()

    def render(self, **context):
        """@API
        Render the template
        @params:
            **context: The context for rendering.
        @returns:
            (str): The rendered string
        """
        _check_vars(context)
        final_context = self.envs.copy()
        final_context.update(context)

        finalcode, funcname = self.parser.assemble(final_context)
        strcode = str(finalcode)
        ret = None
        try:
            execode = compile(strcode, LIQUID_COMPILED_SOURCE_NAME, 'exec')
            localns = {}
            exec(execode, None, localns) # pylint: disable=exec-used
            ret = localns[funcname](final_context)
            # only show when no exception raised
            LOGGER.debug("The compiled code:\n%s", strcode)
        except BaseException as exc: # pylint: disable=broad-except
            _render_failed(exc, finalcode, final_context)
        return ret
