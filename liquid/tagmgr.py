"""A tag manager for liquidpy"""
from .exceptions import TagRegistryException

# The registry for all tags
TAGS = {}

def get_tag(tagname, tagdata, tagcontext):
    """Get the Tag object by given tag name and data

    Args:
        tagname (str): The tag name
        tagdata (str): The tag data
    Returns:
        Tag: The Tag object
    """
    if tagname not in TAGS:
        raise TagRegistryException(tagname)
    return TAGS[tagname](tagname, tagdata, tagcontext)

def register_tag(tagname, tag):
    """Register a tag to the registry

    Args:
        tagname (str): The tag name
        tag (class): A subclass of `Tag` (Not the instance!)
    """
    TAGS[tagname] = tag

def register(*tagnames):
    """Decorator version of register_tag
    If not tagnames given, it will be inferred from the class name
    """
    if len(tagnames) == 1 and callable(tagnames[0]):
        cls = tagnames[0]
        tagname = cls.__name__.lower()
        if tagname.startswith('tag'):
            tagname = tagname[3:]
        TAGS[tagname] = cls
        return cls

    def decorator(cls):
        for tagname in tagnames:
            TAGS[tagname] = cls
        return cls
    return decorator

def unregister_tag(tagname):
    """Unregister a tag from the registry"""
    del TAGS[tagname]

def enable_tag(tagname):
    """Enable a disabled tag"""
    key = f"disabled::{tagname}"
    if key not in TAGS:
        raise TagRegistryException(
            f"Tag is unregisted or already enabled: {tagname}"
        )
    tag = TAGS[key]
    TAGS[tagname] = TAGS.pop(key)

def disable_tag(tagname):
    """Disable a tag"""
    key = f"disabled::{tagname}"
    if key in TAGS or tagname not in TAGS:
        raise TagRegistryException(
            f"Tag is unregisted or already disabled: {tagname}"
        )
    tag = TAGS[tagname]
    TAGS[key] = TAGS.pop(tagname)
