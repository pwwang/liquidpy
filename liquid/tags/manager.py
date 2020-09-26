"""The tag manager

Attributes:
    tag_manager: The tag manager
"""
from ..utils import Singleton
from ..exceptions import LiquidTagRegistryException

class TagManager(Singleton):
    """The tag manager

    Attributes:
        INSTANCE: The instance of this singleton class
        tags: The tags database
    """
    INSTANCE = None # type: TagManager
    tags = {}       # type: Dict[str, Tag]


    def register(self, tag_class_or_alias=None, mode='standard'):
        # type: (Union[Type[Tag], str], bool) -> Callable
        """Register a tag

        This can be worked as a decorator

        Args:
            tag_class_or_alias: The tag class or the alias for the tag class
                to decorate
            mode: Whether do it for given mode

        Returns:
            The decorator or the decorated class
        """
        # if mode == 'jekyll':
        #     from .jekyll.tags import tag_manager as tmgr
        #     return tmgr.register(tag_class_or_alias)
        if mode == 'python':
            from ..python.tags import tag_manager as tmgr
            return tmgr.register(tag_class_or_alias)

        def decorator(tag_class):
            """The decorator for the tag class"""
            name = tag_class.__name__
            if name.startswith('Tag'):
                name = name[3:]
                # keep all-uppercase names, they are special tags
                # like LITERAL, COMMENT, OUTPUT
                if not name.isupper():
                    name = name.lower()
            name = [name]

            if tag_class_or_alias and tag_class is not tag_class_or_alias:
                names = tag_class_or_alias
                if isinstance(names, str):
                    names = (alias.strip() for alias in names.split(','))
                name = names

            for nam in name:
                self.__class__.tags[nam] = tag_class
            return tag_class

        if callable(tag_class_or_alias):
            return decorator(tag_class_or_alias)

        return decorator

    def unregister(self, tagname, mode='standard'):
        # type: (str, bool) -> Type[Tag]
        """Unregister a tag

        Args:
            tagname: The name of the tag to unregister
            mode: Whether do it for given mode

        Returns:
            The tag class unregistered. It can be used to be re-registered
        """
        # if mode == 'jekyll':
        #     from .jekyll.tags import tag_manager as tmgr
        #     return tmgr.unregister(tagname)
        if mode == 'python':
            from ..python.tags import tag_manager as tmgr
            return tmgr.unregister(tagname)

        try:
            return self.tags.pop(tagname)
        except KeyError:
            raise LiquidTagRegistryException(
                f'No such tag: {tagname}'
            ) from None

    def get(self, name):
        # type: (str) -> Optional[Tag]
        """Get the tag class

        Args:
            name: The name of the tag

        Returns:
            The tag class or None if name does not exist
        """
        tagname = name[3:] if name.startswith('end') else name  # type: str

        if tagname not in self.tags:
            return None
        return self.tags[tagname if tagname == name else 'END']

# pylint: disable=invalid-name
tag_manager = TagManager() # type: TagManager
