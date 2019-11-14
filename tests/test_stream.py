import pytest
import io
from liquid import stream

@pytest.mark.parametrize('words, expected', [
	(['a', 'b'], [{'a': 1, 'b':1}]),
	(['aa', 'ab'], [{'a': 0}, {'a': 1, 'b':1}]),
	(['{%', '{%-', '{{'], [{'{':0}, {'%':1, '{': 1}, {'-': 1}]),
])
def test_words_to_matrix(words, expected):
	assert stream.words_to_matrix(words) == expected


def test_stream_unicode():
	stm = stream.LiquidStream.from_string('abìcd')
	assert stm.next() == 'a'
	assert stm.next() == 'b'
	assert stm.next() == 'ì'
	assert stm.next() == 'c'
	assert stm.next() == 'd'
	assert stm.eos()

	stm = stream.LiquidStream.from_string('ab\ìcd')
	assert stm.next() == 'a'
	assert stm.next() == 'b'
	assert stm.next() == '\\'
	assert stm.next() == 'ì'
	assert stm.next() == 'c'
	assert stm.next() == 'd'
	assert stm.eos()


def test_stream_init(tmp_path):
	string = io.StringIO('abc')
	stm = stream.LiquidStream(string)
	assert stm.stream is string
	assert stm.cursor == 0

	stm = stream.LiquidStream.from_stream(string)
	assert stm.stream is string
	assert stm.cursor == 0

	stm = stream.LiquidStream.from_string('abc')
	assert stm.next() == 'a'
	assert stm.next() == 'b'
	assert stm.next() == 'c'
	assert stm.next() == ''

	stm.close()
	assert stm.stream.closed

	sfile = tmp_path.with_suffix('.stream')
	sfile.write_text('abc')
	stm = stream.LiquidStream.from_file(sfile)
	assert stm.next() == 'a'
	assert stm.next() == 'b'
	assert stm.next() == 'c'
	assert stm.next() == ''

	stm.rewind()
	assert stm.cursor == 0
	assert not stm.eos()
	assert stm.next() == 'a'
	assert not stm.eos()
	assert stm.next() == 'b'
	assert not stm.eos()
	assert stm.next() == 'c'
	assert stm.eos()
	assert stm.next() == ''

	stm.close()
	assert stm.stream.closed

@pytest.mark.parametrize('string,words,greedy,expected,nextchar', [
	("abcdefgh", ["x"], False, ("abcdefgh", None), ""),
	("abcdefgh", ["x"], True, ("abcdefgh", None), ""),
	("abcdefgh", ["f", "g"], False, ("abcde", "f"), "g"),
	("abcdefgh", ["f", "g"], True, ("abcde", "f"), "g"),
	("abcdefgh", ["f", "fg"], False, ("abcde", "f"), "g"),
	("abcdefgh", ["f", "fg"], True, ("abcde", "fg"), "h"),
	("abcdefghi", ["f", "fg", "fgi"], True, ("abcde", "fg"), "h"),
	("abcdefghi", ["fgk", "fgl", "fgi"], True, ("abcdefghi", None), ""),
	("abcdefghi", ["f", "fg", "fgi"], False, ("abcde", "f"), "g"),
	("abcdefghi", ["f", "fg", "fgi"], True, ("abcde", "fg"), "h"),
	("abc{%-def", ["{%", "{%-", "{{"], True, ("abc", "{%-"), "d"),
	("abc{%-def", ["{%", "{%-", "{{"], False, ("abc", "{%"), "-"),
	("abc\\{%-def", ["{%", "{%-", "{{"], False, ("abc\\{%-def", None), ""),
	("abc\\\\{%-def", ["{%", "{%-", "{{"], True, ("abc\\\\", "{%-"), "d"),
	("abc'{%-'def", ["{%", "{%-", "{{"], True, ("abc'{%-'def", None), ""),
	("abc\"'\"{%-'def", ["{%", "{%-", "{{"], True, ("abc\"'\"", "{%-"), "'"),
	("abc({%-)def", ["{%", "{%-", "{{"], True, ("abc({%-)def", None), ""),
	("%}", ["%}", "-%}"], True, ("", "%}"), ""),
	("a ,b", [","], False, ("a ", ","), "b")
])
def test_until(string, words, greedy, expected, nextchar):
	s = stream.LiquidStream.from_string(string)
	assert s.until(words, greedy) == expected
	assert s.next() == nextchar

def test_until_until1():
	string = stream.LiquidStream.from_string('mark: special job{{job.index}}" > {{job.outdir}}\\/job.report.data.yaml')
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == 'mark: special job'
	assert tag == '{{'
	leading, tag = string.until(['}}', '-}}'])
	assert leading == 'job.index'
	assert tag == '}}'
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == '" > '
	assert tag == '{{'
	leading, tag = string.until(['}}', '-}}'])
	assert leading == 'job.outdir'
	assert tag == '}}'
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == '\\/job.report.data.yaml'
	assert tag == None


def test_until_until_unicode():
	string = stream.LiquidStream.from_string('mark: specìal job{{job.index}}" > {{job.outdir}}\\/job.report.data.yaml')
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == 'mark: specìal job'
	assert tag == '{{'
	leading, tag = string.until(['}}', '-}}'])
	assert leading == 'job.index'
	assert tag == '}}'
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == '" > '
	assert tag == '{{'
	leading, tag = string.until(['}}', '-}}'])
	assert leading == 'job.outdir'
	assert tag == '}}'
	leading, tag = string.until(['{{', '{{-'], wraps = [], quotes = [])
	assert leading == '\\/job.report.data.yaml'
	assert tag == None

def test_until_until2():
	string = stream.LiquidStream.from_string(
		'{% mode loose -%}\n{% assign my_variable = "tomato" %}{{ my_variable }}')
	leading, tag = string.until(['{%', '{%-', '{{'])
	assert leading == ''
	assert tag == '{%'
	leading, tag = string.until(['%}', '-%}', '}}'])
	assert leading == ' mode loose '
	assert tag == '-%}'
	leading, tag = string.until(['{%', '{%-', '{{'])
	assert leading == '\n'
	assert tag == '{%'
	leading, tag = string.until(['%}', '-%}', '}}'])
	assert leading == ' assign my_variable = "tomato" '
	assert tag == '%}'
	leading, tag = string.until(['{%', '{%-', '{{'])
	assert leading == ''
	assert tag == '{{'
	leading, tag = string.until(['%}', '-%}', '}}'])
	assert leading == ' my_variable '
	assert tag == '}}'
	leading, tag = string.until(['{%', '{%-', '{{'])
	assert leading == ''
	assert tag == None

def test_until_until2():
	string = stream.LiquidStream.from_string("spec\ìal{{a}}")
	leading, tag = string.until(['{{'])
	assert leading == "spec\ìal"
	assert tag == '{{'
	leading, tag = string.until(['}}'])
	assert leading == "a"
	assert tag == '}}'

@pytest.mark.parametrize('string,delimit,limit,trim,expected', [
	('', ',', 0, True, ['']),
	('a,b,c,d', ',', 0, True, ['a','b','c','d']),
	('a,b,c,d', ',', 1, True, ['a','b,c,d']),
	('a, b, c, d', ',', 2, True, ['a','b','c, d']),
	('a, "b, c", d', ',', 2, False, ['a',' "b, c"', ' d']),
])
def test_split(string, delimit, limit, trim, expected):
	s = stream.LiquidStream.from_string(string)
	assert s.split(delimit, limit, trim) == expected
