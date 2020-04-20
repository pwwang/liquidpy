import pytest
import logging

from liquid.code import LiquidLine, LiquidCode
from liquid.parser import LiquidParser, _multi_line_support
from liquid.config import LiquidConfig
from liquid.stream import LiquidStream
from liquid.defaults import LIQUID_DEFAULT_MODE, LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidSyntaxError

@pytest.fixture(scope = "function")
def liqparser():
	precode = LiquidCode()
	code = LiquidCode()
	stream = LiquidStream.from_string("abcde")
	return LiquidParser(stream=stream, shared_code=precode, code=code, filename='', prev=None, config=LiquidConfig(
		mode='compact', loglevel='detail',include='',extends=None
	))

def test_parser_init():
	precode = LiquidCode()
	code = LiquidCode()
	stream = LiquidStream.from_string("abcde")
	lp = LiquidParser(stream=stream, shared_code=precode, code=code, prev=None,config=None,filename='')
	assert lp.stream is stream
	assert lp.config is None
	assert lp.context.stacks == []
	assert lp.shared_code is precode
	assert lp.code is code
	assert lp.endtag is None

def test_parser_parse_for(liqparser):
	liqparser.stream = LiquidStream.from_string('for a in b')
	with pytest.raises(LiquidSyntaxError) as ex:
		liqparser.parse_statement('{%')
	assert "Expecting a closing tag for '{%'" in str(ex.value)

	liqparser.stream = LiquidStream.from_string('for a in b %} aa')
	liqparser.parse_statement('{%')
	#print(liqparser.meta['code'])

def test_parser_parse_mode(liqparser):
	liqparser.stream = LiquidStream.from_string('config mode=loose, loglevel=debug -%}')
	liqparser.parse_statement('{%')
	assert liqparser.config.mode == 'loose'
	assert logging.getLevelName(logging.getLogger(LIQUID_LOGGER_NAME).level) == 'DEBUG'

def test_liquidline():
	ll = LiquidLine("abcde")
	assert repr(ll) == "<LiquidLine 'abcde'>"

def test_multiline_support_func():
	assert _multi_line_support("""     a
		b
			c    """) == """     a b c    """