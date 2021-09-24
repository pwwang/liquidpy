"""Provides a base extension class"""
import re
from base64 import b64encode
from typing import TYPE_CHECKING

from jinja2 import nodes
from jinja2.ext import Extension

if TYPE_CHECKING:
    from jinja2.parser import Parser


re_e = re.escape
re_c = lambda rex: re.compile(rex, re.M | re.S)

# A unique id to encode the start strings
ENCODING_ID = id(Extension)


class LiquidExtension(Extension):
    """A base extension class for extensions in this package to extend"""

    def __init_subclass__(cls) -> None:
        """Initalize the tags and raw_tags using tag manager"""
        cls.tags = cls.tag_manager.names
        cls.raw_tags = cls.tag_manager.names_raw

    def preprocess(  # type: ignore
        self,
        source: str,
        name: str,
        filename: str,
    ) -> str:
        """Try to keep the tag body raw by encode the variable/comment/block
        start strings ('{{', '{#', '{%') so that the body won't be tokenized
        by jinjia.
        """
        if not self.__class__.raw_tags:  # pragma: no cover
            return super().preprocess(source, name, filename=filename)

        block_start_re = re_e(self.environment.block_start_string)
        block_end_re = re_e(self.environment.block_end_string)
        variable_start_re = re_e(self.environment.variable_start_string)
        comment_start_re = re_e(self.environment.comment_start_string)
        to_encode = re_c(
            f"({block_start_re}|{variable_start_re}|{comment_start_re})"
        )

        def encode_raw(matched):
            content = to_encode.sub(
                lambda m: (
                    f"$${ENCODING_ID}$"
                    f"{b64encode(m.group(1).encode()).decode()}$$"
                ),
                matched.group(2),
            )
            return f"{matched.group(1)}{content}{matched.group(3)}"

        for raw_tag in self.__class__.raw_tags:
            tag_re = re_c(
                # {% comment "//"
                fr"({block_start_re}(?:\-|\+|)\s*{raw_tag}\s*.*?"
                # %}
                fr"(?:\-{block_end_re}|\+{block_end_re}|{block_end_re}))"
                # ...
                fr"(.*?)"
                # {% endcomment
                fr"({block_start_re}(?:\-|\+|)\s*end{raw_tag}\s*"
                fr"(?:\-{block_end_re}|\+{block_end_re}|{block_end_re}))"
            )
            source = tag_re.sub(encode_raw, source)
        return source

    def parse(self, parser: "Parser") -> nodes.Node:
        """Let tag manager to parse the tags that are being listened to"""
        token = next(parser.stream)
        return self.__class__.tag_manager.parse(
            self.environment, token, parser
        )
