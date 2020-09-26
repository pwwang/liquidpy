"""About tags inherited from standard mode

Attributes
    BASE_GRAMMAR: The base grammar for python mode
    tag_manager: The tag manager for python mode
"""
from pathlib import Path
from ...tags.manager import TagManager as TagManagerStandard
from ...tags.grammar import Grammar
from ...tags.tag import Tag as TagStandard

BASE_GRAMMAR = Grammar(Path(__file__).parent / 'grammar.lark') # type: Grammar

class TagManager(TagManagerStandard):
    """Tag manager for tags in python mode"""
    INSTANCE = None
    tags = {}

# pylint: disable=invalid-name
tag_manager = TagManager() # type: TagManager

class Tag(TagStandard, use_parser=True):
    """The base tag class for tags in python mode"""
    BASE_GRAMMAR = BASE_GRAMMAR
