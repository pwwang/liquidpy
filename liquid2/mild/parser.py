from lark import v_args
from ..common.parser import Parser, Transformer, try_direct_tag
from ..common.tagmgr import get_tag
from ..common.exception import EndTagUnexpected
# load tags
from . import tags

@v_args(inline=True)
class MildTransformer(Transformer):

    @try_direct_tag
    def open_tag(self, tagstr):
        tagname, tagargs = self._clean_tagstr(tagstr)
        return get_tag(tagname, tagargs)

    def close_tag(self, tagstr):
        tagname, tagargs = self._clean_tagstr(tagstr)
        tagname = tagname[3:]
        if not self._stacks or self._stacks[-1].name != tagname:
            raise EndTagUnexpected(f'end{tagname}')
        self._stacks.pop()

    def literal_tag_both_compact(self, tagstr):
        return tagstr.strip()

    def literal_tag_left_compact(self, tagstr):
        return tagstr.lstrip()

    def literal_tag_right_compact(self, tagstr):
        return tagstr.rstrip()

    def literal_tag_non_compact(self, tagstr):
        return tagstr

    literal_tag_first = literal_tag_non_compact
    literal_tag_first_right_compact = literal_tag_right_compact

class MildParser(Parser):

    GRAMMER = r"""
    start: tag*

    ?tag: output_tag | raw_tag | open_tag | close_tag | literal_tag

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

    LITERAL_TAG_BOTH_COMPACT.-99: /(?<=-[\}%]\}).+?(?=\{[\{%]-)/s
    LITERAL_TAG_LEFT_COMPACT.-99: /(?<=-[\}%]\}).+?(?=\{[\{%][^\-]|$)/s
    LITERAL_TAG_RIGHT_COMPACT.-99: /(?<=[^\-][\}%]\}).+?(?=\{[\{%]-)/s
    LITERAL_TAG_NON_COMPACT.-99: /(?<=[^\-][\}%]\}).+?(?=\{[\{%][^\-]|$)/s
    LITERAL_TAG_FIRST.-99: /^.+?(?=\{[\{%]|$)/s
    LITERAL_TAG_FIRST_RIGHT_COMPACT.-99: /^.+?(?=\{[\{%][^\-]|$)/s
    OUTPUT_TAG: /\{\{-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?\}\}/s
    CLOSE_TAG.2: /\{%-?\s*end.*?-?%\}/s
    OPEN_TAG: /\{%-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?%\}/s
    RAW_TAG: /\{%-?\s*raw\s*-?%\}.*?\{%-?\s*endraw\s*-?%\}/s
    """

    TRANSFORMER = MildTransformer()

mild_parser = MildParser()

