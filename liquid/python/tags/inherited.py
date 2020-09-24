from pathlib import Path
from ...tags.manager import TagManager as TagManagerStandard
from ...tags.grammar import Grammar
from ...tags.tag import Tag as TagStandard

BASE_GRAMMAR = Grammar(Path(__file__).parent / 'grammar.lark')

class TagManager(TagManagerStandard):

    INSTANCE = None
    tags = {}

tag_manager = TagManager()

class Tag(TagStandard, use_parser=True):

    BASE_GRAMMAR = BASE_GRAMMAR
