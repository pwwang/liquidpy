import pytest
import logging

from liquid.parser import LiquidLine, LiquidCode, LiquidParser
from liquid.stream import LiquidStream
from liquid.defaults import LIQUID_DEFAULT_MODE, LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidSyntaxError

@pytest.fixture(scope = "function")
def liqparser():
	precode = LiquidCode()
	code = LiquidCode()
	stream = LiquidStream.from_string("abcde")
	return LiquidParser(stream, precode, code, '')

def test_parser_init():
	precode = LiquidCode()
	code = LiquidCode()
	stream = LiquidStream.from_string("abcde")
	lp = LiquidParser(stream, precode, code, '')
	assert lp.stream is stream
	assert lp.mode == LIQUID_DEFAULT_MODE
	assert lp.stack == []
	assert lp.precode is precode
	assert lp.code is code
	assert lp.endtag is None
	assert len(lp.nodes) > 0

def test_parser_parse_for(liqparser):
	liqparser.stream = LiquidStream.from_string('for a in b')
	with pytest.raises(LiquidSyntaxError) as ex:
		liqparser.parse_statement('{%')
	assert "Expecting a closing tag for '{%'" in str(ex.value)

	liqparser.stream = LiquidStream.from_string('for a in b %} aa')
	liqparser.parse_statement('{%')
	#print(liqparser.meta['code'])

def test_parser_parse_mode(liqparser):
	liqparser.stream = LiquidStream.from_string('mode compact debug -%}')
	liqparser.parse_statement('{%')
	assert liqparser.mode == 'compact'
	assert logging.getLevelName(logging.getLogger(LIQUID_LOGGER_NAME).level) == 'DEBUG'

def test_liquidline():

	ll = LiquidLine("abcde")
	assert repr(ll) == "<LiquidLine 'abcde' (compiled from #0)>"

def test_multiline_support_func():
	assert LiquidParser._multi_line_support("""     a
		b
			c    """) == """     a b c    """