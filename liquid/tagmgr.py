"""A tag manager for liquidpy"""
from functools import wraps
from lark import v_args
from .exceptions import TagRegistryException

# The registry for all tags
LIQUID_TAGS = {}

def _load_all_tag_transformers(transformer_class):
    """A decorator function for transformer class to register all
    transformer functions from tags"""
    for tag_class in LIQUID_TAGS.values():
        if not tag_class.TRANSFORMERS:
            continue

        for transformer_func in tag_class.TRANSFORMERS:
            # remove t_ prefix
            transformer_name = transformer_func.__name__[2:]
            setattr(transformer_class, transformer_name, transformer_func)

        tag_class.TRANSFORMERS = None
    return transformer_class

def _load_all_tag_syntaxes(base_grammar):
    """Decorator function for parser to load all syntax from tags"""
    def wrapper(parser_class):
        parser_class.GRAMMAR = base_grammar
        for tag_class in LIQUID_TAGS.values():
            if not tag_class.SYNTAX:
                continue
            base_grammar.update(tag_class.SYNTAX)
            tag_class.SYNTAX = None
        return parser_class
    return wrapper


def get_tag(tagname, tagdata, tagcontext):
    """Get the Tag object by given tag name and data

    Args:
        tagname (str): The tag name
        tagdata (str): The tag data
    Returns:
        Tag: The Tag object
    """
    if tagname not in LIQUID_TAGS:
        raise TagRegistryException(f'No such tag: {tagname}')
    return LIQUID_TAGS[tagname](tagname, tagdata, tagcontext)

def _tag_class_decorator(cls, tagnames):
    # register tag
    for tagname in tagnames:
        LIQUID_TAGS[tagname] = cls

    # replace tagnames in syntax
    if len(tagnames) == 1:
        cls.SYNTAX = cls.SYNTAX and cls.SYNTAX.replace(
            '$tagnames',
            f'"{tagnames[0]}"'
        )
    else:
        cls.SYNTAX = cls.SYNTAX and cls.SYNTAX.replace(
            '$tagnames',
            '(%s)' % (f'"{tagname}"' for tagname in tagnames)
        )

    # register transformers
    cls.TRANSFORMERS = []
    for key, val in cls.__dict__.items():
        if key.startswith('t_'):
            cls.TRANSFORMERS.append(val)

    # we don't need them for the tag class
    for transformer in cls.TRANSFORMERS:
        delattr(cls, transformer.__name__)

    return cls

def register_tag(*tagnames):
    """Decorator to register a tag
    If not tagnames given, it will be inferred from the class name
    """

    if len(tagnames) == 1 and callable(tagnames[0]):
        cls = tagnames[0]
        tagname = cls.__name__.lower()
        if tagname.startswith('tag'):
            tagname = tagname[3:]
        return _tag_class_decorator(cls, tagnames=[tagname])

    return lambda cls, tagnames=tagnames: _tag_class_decorator(cls, tagnames)

def register_tag_external(*tagnames, extended=False):
    """Register an external tag

    Since all internal tags have already been registered, so we
    need to load the syntax and transformers from the external tag"""
    parsers = []
    if not extended or extended == 'both':
        from .parser import StandardParser
        parsers.append(StandardParser)
    if extended: # True/both
        from .extended.parser import ExtendedParser
        parsers.append(ExtendedParser)

    def decorator(cls, tagnames=tagnames):
        cls = _tag_class_decorator(cls, tagnames=tagnames)
        for parser in parsers:
            parser.TRANSFORMER = v_args(inline=True)(
                _load_all_tag_transformers(parser.TRANSFORMER)
            )
            _load_all_tag_syntaxes(parser.GRAMMAR)(parser)
        return cls

    if len(tagnames) == 1 and callable(tagnames[0]):
        cls = tagnames[0]
        tagname = cls.__name__.lower()
        if tagname.startswith('tag'):
            tagname = tagname[3:]
        return decorator(cls, tagnames=[tagname])

    return decorator

def unregister_tag(tagname):
    """Unregister a tag from the registry"""
    tag_class = LIQUID_TAGS[tagname]

    @wraps(tag_class.render)
    def render(self, local_envs, global_envs):
        raise TagRegistryException(f"Unregistered tag: {tagname}")

    tag_class.render = render
