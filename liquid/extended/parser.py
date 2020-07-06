"""Parser for extended rules"""

from lark import v_args
from ..parser import TagFactory, Parser
from ..tagmgr import load_all_tags
from ..grammar import BASE_GRAMMAR

# for external use
EXTENDED_GRAMMAR = BASE_GRAMMAR.copy()

def _extend_grammar(grammar):
    pass

class ExtendedTagFactory(TagFactory):
    """Tag factory (transformers) for extended parser"""

@load_all_tags(_extend_grammar(EXTENDED_GRAMMAR))
class ExtendedParser(Parser):
    """Parser for extended liquid"""
    TRANSFORMER = ExtendedTagFactory
