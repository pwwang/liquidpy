"""Utilities for liquidpy"""
import logging
from io import StringIO
from pathlib import Path
from textwrap import shorten as tw_shorten
from collections import namedtuple
from rich.logging import RichHandler
from rich.syntax import Syntax
from rich.console import Console
from lark import Lark
from .config import (LIQUID_LOGGER_NAME,
                     LIQUID_EXC_MAX_STACKS,
                     LIQUID_EXC_CODE_CONTEXT)
from .exceptions import LiquidNameError

TemplateMeta = namedtuple('TemplateMeta',
                          ['name', 'path', 'stream', 'should_close'])

class Nothing:
    # pylint: disable=too-few-public-methods
    """A unique object to identify a NOTHING other than None

    Lark transformers sometimes can pass None or nothing when no
    terminals matched. To distinguish this situation, we need something
    other than None.
    """
    def __repr__(self):
        return 'NOTHING'

NOTHING = Nothing()

class _PositionalTuple(tuple):
    def __new__(cls, *args):
        return super().__new__(cls, args)

class OptionalTags(_PositionalTuple):
    """Indicates the arguments are optional"""

class RequiredTags(_PositionalTuple):
    """Indicates the arguments are required"""

class Singleton:
    # pylint: disable=too-few-public-methods
    """An abstract base class for signleton classes

    To prevent the __init__ to run again for initialized object from __new__,
    we have a property `_initialized` to inidicate whether the object has been
    initialized already.
    """
    INSTANCE = None # type: Optional[Type[Singleton]]


    def __new__(cls, *args, **kwargs): # pylint: disable=unused-argument
        if cls.INSTANCE is None:
            cls.INSTANCE = object.__new__(cls)
            cls.INSTANCE._initialized = False
            return cls.INSTANCE
        return cls.INSTANCE

    def __init__(self, *args, **kwargs):
        # pylint: disable=access-member-before-definition
        if not self._initialized:
            self._initialized = True
            self._init(*args, **kwargs)

    def _init(self, *args, **kwargs):
        """Initialize the object here"""


def template_meta(template):
    # type: (Union[IO, str, Path]) -> NamedTuple
    """Get the metadata of a template

    This is to try to normalize the template for liquid into the name of
    the template, the IO object and whether we should close that IO object.

    The IO object should be closed when a valid path is passed.

    Args:
        template: The template

    Returns:
        A tuple of the template name, the IO object and
            whether we should close that IO object
    """
    if isinstance(template, str):
        path = None # type: Optional[Path]
        try:
            path = Path(template)
            if not path.is_file():
                raise OSError
        except OSError:
            # filename too long or other OSError
            path = None

        if not path:
            return TemplateMeta('<string>',
                                f'<string> ({shorten(template, 20)})',
                                StringIO(template),
                                True)

        return TemplateMeta(path.stem, str(path), path.open(), True)

    if isinstance(template, Path):
        return TemplateMeta(template.stem, str(template), template.open(), True)

    # IO object
    name = '<unknown>' # type: str
    try:
        name = template.name
    except AttributeError: # pragma: no cover
        pass

    return TemplateMeta(name, name, template, False)

def check_name(names):
    # type: (Iterator[str]) -> None
    """Check whether the name is allowed

    Raises:
        LiquidNameError: when names contains name that is not allowed
    """
    for name in names:
        if name.startswith('__LIQUID'):
            raise LiquidNameError(f'Name is preserved for liquid: {name!r}')

def analyze_leading_spaces(string):
    # type: (str) -> Tuple[int, int]
    """Analyze the leading spaces of a string

    Args:
        string: The string to analyze

    Returns:
        A tuple of two integers. Number of new lines and the number spaces
        that last new line has
    """
    newline = 0
    last_nspaces = 0
    for char in string:
        if not char.isspace():
            break
        if char == '\n':
            newline += 1
            last_nspaces = 0
        last_nspaces += 1
    return newline, last_nspaces

def shorten(text, width, placeholder=' ...'):
    # type: (str, int, str) -> str
    """Wrap textwrap.shorten

    Since textwrap.shorten('abcdefg', 5, placeholder='.') will return '.'
    But what we want is 'abcd.'
    """
    if len(text) <= width:
        return text
    string_to_check = text[:width - len(placeholder) + 1]
    if any(char.isspace() for char in string_to_check):
        return tw_shorten(text, width, placeholder=placeholder)
    return string_to_check[:-1] + placeholder

def _exc_stack_code(context):
    # type: (Diot) -> str
    console = Console(file=StringIO())
    console.print(f"{context.path!r}, line {context.lineno + 1}, "
                  f"column {context.colno + 1}")

    stream = context.stream
    seekable = False
    if stream.closed:
        try:
            if isinstance(stream, StringIO):
                stream = StringIO(stream.getvalue())
            else:
                stream = open(stream.name)
            seekable = stream.seekable()
        except (AttributeError, FileNotFoundError, IOError, ValueError):
            seekable = False
    else:
        try:
            seekable = stream.seekable()
        except (AttributeError, ValueError, IOError):
            seekable = False

    if not seekable:
        console.print("  [Stream not seekable]") # pragma: no cover
    else:
        stream.seek(0)
        line_range = (
            max(0, context.lineno - LIQUID_EXC_CODE_CONTEXT) + 1,
            context.lineno + LIQUID_EXC_CODE_CONTEXT + 1
        )
        code = Syntax(stream.read(),
                      lexer_name='liquid',
                      line_numbers=True,
                      line_range=line_range,
                      highlight_lines={context.lineno + 1})
        console.print(code)
    return console.file.getvalue() + "\n"

def excmsg_with_context(msg, context, parser):
    # type: (str, Diot, Parser) -> str
    """Assemble the exception message with context

    Args:
        context: The context
        parser: The parser

    Returns:
        The assembled exception message
    """
    config = parser.config if parser else None
    if not context or not config: # or not config.debug:
        return msg

    stacks = [context]
    for _ in range(LIQUID_EXC_MAX_STACKS - 1):
        parent = parser.parent
        if not parent:
            break
        stacks.insert(0, parent.context)

    msgs = [msg, '']
    for stack in stacks:
        msgs.append(_exc_stack_code(stack))
    return '\n'.join(msgs)

def get_tag_parser(start, grammar, transformer, base_grammar=None):
    # type: (Union[str, Path], TagTransformer, str, Optional[Grammar]) -> Lark
    """Get the lark parser for tags

    Args:
        start: The start rule name
        grammar: The new grammar
        transformer: The transformer for the parser
        base_grammar: The base grammar

    Returns:
        The lark object for parsing
    """
    if base_grammar and grammar:
        lark_grammar = base_grammar.copy()
        lark_grammar.update(grammar)
    elif base_grammar:
        lark_grammar = base_grammar
    else: # pragma: no cover
        from .tags.grammar import Grammar
        lark_grammar = Grammar(grammar)

    return Lark(str(lark_grammar),
                parser='lalr',
                start=start,
                debug=False,
                maybe_placeholders=True,
                # pylint: disable=not-callable
                transformer=transformer)

def find_template(path, curr_path, config_paths):
    # type: (str, Optional[Union[str, Path]], List[Union[str, Path]])
    #   -> Optional[Path]
    """Find the template by given path

    curr_path will always be the first one to look up. If it is None (template
    from a string, for example), current working directory will be used.

    Args:
        path: The path to look up
        curr_path: The path where current template is located
        config_paths: The paths from configuration

    Returns:
        The path found either directory.
    """
    path = Path(path)
    if path.is_absolute():
        return path

    if not curr_path: # pragma: no cover
        curr_path = Path('.')
    else:
        curr_path = Path(curr_path).parent

    config_paths = config_paths + [curr_path]
    for cpath in config_paths:
        thepath = Path(cpath) / path
        if thepath.is_file():
            return thepath
    return None

def find_dir(path, curr_path):
    # type: (str, Optional[Union[str, Path]]) -> Optional[Path]
    """Find the directory by given path

    If path is relative, find one relative to curr_path.

    Args:
        path: The path to look up
        curr_path: the path where current template is located

    Returns:
        The directory found
    """
    path = Path(path)
    if path.is_absolute():
        return path

    curr_path = Path(curr_path).parent if curr_path else Path('.')

    ret = curr_path / path
    return ret if ret.is_dir() else None

# pylint: disable=invalid-name
logger = logging.getLogger(LIQUID_LOGGER_NAME)
logger.addHandler(RichHandler(show_time=False, show_path=False))
