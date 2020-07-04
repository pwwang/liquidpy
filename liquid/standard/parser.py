"""The top-level parser for the whole template
This will obey the rules from shopify's standard liquid engine
"""
from lark import v_args
# loading tags. Must import before tagmgr
from . import tags # pylint: disable=unused-import
from ..tagmgr import _load_all_tag_transformers, _load_all_tag_syntaxes
from ..parser import TagFactory, Parser
from ..grammar import BASE_GRAMMAR

@v_args(inline=True)
@_load_all_tag_transformers
class StandardTagFactory(TagFactory):
    """Tag factory (transformers) for standard parser"""

@_load_all_tag_syntaxes(BASE_GRAMMAR)
class StandardParser(Parser):
    TRANSFORMER = StandardTagFactory
