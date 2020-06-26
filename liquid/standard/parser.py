"""The top-level parser for the whole template
This will obey the rules from shopify's standard liquid engine
"""
from lark import v_args
from ..common.parser import Parser, Transformer
from ..tagmgr import get_tag
# load tags
# pylint: disable=unused-import
from . import tags

@v_args(inline=True)
class StandardTransformer(Transformer):
    """Transformer for the standard parser"""
    def open_tag(self, tagstr):
        """Open a tag"""
        tagname, tagdata = self._clean_tagstr(tagstr)
        tag = get_tag(tagname, tagdata, self._tag_context(tagstr))
        self._opening_tag(tag)
        return tag

    def literal_tag_both_compact(self, tagstr):
        """Literal with both end compact"""
        return tagstr.update(tagstr.strip())

    def literal_tag_left_compact(self, tagstr):
        """Literal with left end compact"""
        return tagstr.update(tagstr.lstrip())

    def literal_tag_right_compact(self, tagstr):
        """Literal with right end compact"""
        return tagstr.update(tagstr.rstrip())

    def literal_tag_non_compact(self, tagstr):
        """Literal with no compact"""
        return tagstr

    literal_tag_first = literal_tag_non_compact
    literal_tag_first_right_compact = literal_tag_right_compact

class StandardParser(Parser):
    """The standard parser with rules from shopify's liquid"""

    GRAMMAR = r"""
    start: tag*

    ?tag: output_tag | raw_tag | close_tag | open_tag | literal_tag

    output_tag: OUTPUT_TAG
    raw_tag: RAW_TAG
    open_tag: OPEN_TAG
    close_tag: CLOSE_TAG
    literal_tag: literal_tag_both_compact
        | literal_tag_left_compact
        | literal_tag_right_compact
        | literal_tag_non_compact
        | literal_tag_first

    literal_tag_both_compact: LITERAL_TAG_BOTH_COMPACT
    literal_tag_left_compact: LITERAL_TAG_LEFT_COMPACT
    literal_tag_right_compact: LITERAL_TAG_RIGHT_COMPACT
    literal_tag_non_compact: LITERAL_TAG_NON_COMPACT
    literal_tag_first: LITERAL_TAG_FIRST
    literal_tag_first_right_compact: LITERAL_TAG_FIRST_RIGHT_COMPACT

    LITERAL_TAG_BOTH_COMPACT: /(?<=-[\}%]\}).+?(?=\{[\{%]-)/s
    LITERAL_TAG_LEFT_COMPACT: /(?<=-[\}%]\}).+?(?=\{[\{%][^\-]|$)/s
    LITERAL_TAG_RIGHT_COMPACT: /(?<=[^\-][\}%]\}).+?(?=\{[\{%]-)/s
    LITERAL_TAG_NON_COMPACT: /(?<=[^\-][\}%]\}).+?(?=\{[\{%][^\-]|$)/s
    LITERAL_TAG_FIRST: /^.+?(?=\{[\{%]|$)/s
    LITERAL_TAG_FIRST_RIGHT_COMPACT: /^.+?(?=\{[\{%][^\-]|$)/s
    OUTPUT_TAG: /\{\{-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?\}\}/s
    CLOSE_TAG: /\{%-?\s*end.*?-?%\}/s
    OPEN_TAG: /\{%-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?%\}/s
    RAW_TAG: /\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}/s
    """

    TRANSFORMER = StandardTransformer

# pylint: disable=invalid-name
parse = StandardParser().parse
