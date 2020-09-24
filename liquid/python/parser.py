"""BLock parser to parse the text into blocks in python mode"""
from .tags import tag_manager
from ..parser import Parser as ParserStandard
from ..nodes import (
    Node as NodeStandard,
    NodeTag as NodeTagStandard,
    NodeOutput as NodeOutputStandard,
    NodeScanner as NodeScannerStandard
)

class NodeTag(NodeTagStandard, tag_manager=tag_manager):
    """Node tag for python mode using a different tag manager"""

class NodeComment(NodeStandard, tag_manager=tag_manager):
    """Node comment for python mode"""
    OPEN_TAG = '{#', '{#-'
    CLOSE_TAG = '#}', '-#}'
    name = "COMMENT"

class NodeOutput(NodeOutputStandard, tag_manager=tag_manager):
    """Node output for python mode using a different tag manager"""

class NodeScanner(NodeScannerStandard):
    """Allows NodeComment: {# ... #}"""
    NODES = (NodeComment, NodeOutput, NodeTag)

class Parser(ParserStandard):
    """Parsing text into blocks in python mode"""
    NODESCANNER_CLASS = NodeScanner
