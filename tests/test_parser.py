import pytest
import logging

from liquid.parser import LiquidLine, LiquidCode, LiquidParser
from liquid.stream import Stream
from liquid.defaults import LIQUID_DEFAULT_MODE, LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidSyntaxError

@pytest.fixture(scope = "function")
def liqparser():
	precode = LiquidCode()
	code = LiquidCode()
	stream = Stream.from_string("abcde")
	return LiquidParser(stream, precode, code)

def test_parser_init():
	precode = LiquidCode()
	code = LiquidCode()
	stream = Stream.from_string("abcde")
	lp = LiquidParser(stream, precode, code)
	assert lp.stream is stream
	assert lp.meta['mode'] == LIQUID_DEFAULT_MODE
	assert lp.meta['stack'] == []
	assert lp.meta['precode'] is precode
	assert lp.meta['code'] is code
	assert lp.endtag is None
	assert len(lp.nodes) > 0

def test_parser_parse_for(liqparser):
	liqparser.stream = Stream.from_string('for a in b')
	with pytest.raises(LiquidSyntaxError) as ex:
		liqparser.parse_statement('{%')
	assert "Expecting a closing tag for '{%'" in str(ex.value)

	liqparser.stream = Stream.from_string('for a in b %} aa')
	liqparser.parse_statement('{%')
	#print(liqparser.meta['code'])

def test_parser_parse_mode(liqparser):
	liqparser.stream = Stream.from_string('mode compact debug -%}')
	liqparser.parse_statement('{%')
	assert liqparser.meta['mode'] == 'compact'
	assert logging.getLevelName(logging.getLogger(LIQUID_LOGGER_NAME).level) == 'DEBUG'

def test_liquidline():
	ll = LiquidLine("abcde", 99)
	assert repr(ll) == "<LiquidLine 'abcde' (compiled from #99)>"