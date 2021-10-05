"""Provide tag manager"""
import re
from base64 import b64decode
from typing import TYPE_CHECKING, Callable, Dict, Set, Union

from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError

if TYPE_CHECKING:
    from jinja2.lexer import Token
    from jinja2.parser import Parser
    from jinja2.environment import Environment


from ..exts.ext import ENCODING_ID

ENCODED_PATTERN = re.compile(fr"\$\${ENCODING_ID}\$([\w=+/]+)\$\$")


def decode_raw(body: str) -> str:
    """Decode the encoded string in body

    The start string in body is encoded so that they won't be recognized
    as variable/comment/block by jinja. This way, we can protect the body
    from being tokenized.

    Args:
        body: The body

    Returns:
        The decoded string.
    """
    return ENCODED_PATTERN.sub(
        lambda m: b64decode(m.group(1)).decode(),
        body,
    )


class TagManager:
    """A manager for tags

    Attributes:
        tags: a mapping of tag names and parser functions
        envs: a mapping of tag names and whether environment should be passed
            to the parser functions
        raws: a mapping of tag names and whether the tag body should be
            kept raw.
    """

    __slots__ = ("tags", "envs", "raws")

    def __init__(self) -> None:
        """Constructor"""
        self.tags: Dict[str, Callable] = {}
        self.envs: Dict[str, bool] = {}
        self.raws: Dict[str, bool] = {}

    def register(
        self,
        name_or_tagparser: Union[str, Callable] = None,
        env: bool = False,
        raw: bool = False,
    ) -> Callable:
        """Register a filter

        This can be used as a decorator

        Examples:
            >>> @tag_manager.register
            >>> def comment(token, parser):
            >>>     from jinja2 import nodes
            >>>     return nodes.Const("")

        Args:
            name_or_tagparser: The tag parser to register
                if name is given, will be treated as alias
            env: Whether we should pass environment to the parser
            raw: Whether we should keep the body of the tag raw

        Returns:
            The registered parser for the tag or a decorator
        """

        def decorator(tagparser: Callable) -> Callable:
            name = tagparser.__name__
            name = [name]  # type: ignore

            if (
                name_or_tagparser and name_or_tagparser is not tagparser
            ):  # pragma: no cover
                names = name_or_tagparser
                if isinstance(names, str):
                    names = (
                        nam.strip() for nam in names.split(",")
                    )  # type: ignore
                name = names  # type: ignore

            for nam in name:
                self.tags[nam] = tagparser
                self.envs[nam] = env
                self.raws[nam] = raw

            return tagparser

        if callable(name_or_tagparser):
            return decorator(name_or_tagparser)

        return decorator

    @property
    def names(self) -> Set[str]:
        """Get a set of the tag names"""
        return set(self.tags)

    @property
    def names_raw(self) -> Set[str]:
        """Get a set of names of tags whose body will be kept raw"""
        return set(raw for raw in self.raws if self.raws[raw])

    def parse(
        self, env: "Environment", token: "Token", parser: "Parser"
    ) -> nodes.Node:
        """Calling the parser functions to parse the tags

        Args:
            env: The environment
            token: The token matches the tag name
            parser: The parser

        Returns:
            The parsed node
        """
        tagname = token.value
        if tagname not in self.tags:  # pragma: no cover
            raise TemplateSyntaxError(
                f"Encountered unknown tag '{tagname}'.",
                token.lineno,
            )

        if self.envs.get(tagname, False):
            return self.tags[tagname](env, token, parser)
        return self.tags[tagname](token, parser)
