import pytest
import logging
from pathlib import Path
from liquid import Liquid, _check_envs
from liquid.stream import LiquidStream
from liquid.defaults import LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidWrongKeyWord, LiquidRenderError, LiquidSyntaxError

@pytest.fixture
def debug():
	dbg = Liquid.debug()
	Liquid.debug(True)
	yield
	Liquid.debug(dbg)

@pytest.fixture
def HERE():
	return Path(__file__).parent.resolve()

def test_if_single():
	liq = Liquid("""
{% if a == 1 %}
abc{{b}}
{% endif %}
""")

	assert liq.render(a=1, b=2) == '\n\nabc2\n\n'
	assert str(liq.code) == """  _liquid_ret_append('\\n')
  if a == 1:
    _liquid_ret_extend([
      '\\n',
      'abc',
    ])
    _liquid_ret_append(b)
    _liquid_ret_append('\\n')
  _liquid_ret_append('\\n')
  return ''.join(str(x) for x in _liquid_rendered)
"""

def test_if_multiple():
	liq = Liquid("""
{% if a == 1 \
      and b == 2 %}
abc
{% endif %}
""")

	assert liq.render(a=1, b=2) == '\n\nabc\n\n'

	liq = Liquid("""
{% if "\\n" in a \
      and b == 2 %}
abc
{% endif %}
""")
	assert liq.render(a='a\nb', b=2) == '\n\nabc\n\n'

	liq = Liquid("""
{% mode compact %}
{% if a == 1 %}
abc{{b}}
{% else:%}
cde
{% endif %}
""")
	assert liq.render(a=2) == '\ncde'

	liq = Liquid("""{% mode compact %}
{% if a == 1 %}
abc{{b}}
{% else if a == 2:%}
cde
{% endif %}
""")
	assert liq.render(a=2) == 'cde'

	liq = Liquid("""{% mode compact %}
{% if a == 1 %}
abc{{b}}
{% elseif a == 2:%}
cde
{% endif %}
""")
	assert liq.render(a=2) == 'cde'

	liq = Liquid("""{% mode compact %}
{% if a == 1 %}
abc{{b}}
{% elif a == 2:%}
cde
{% endif %}
""")
	assert liq.render(a=2) == 'cde'

	liq = Liquid("""{% mode compact %}
{% if a == 1 %}
abc{{b}}
{% elsif a == 2:%}
cde
{% endif %}
""")
	assert liq.render(a=2) == 'cde'

def test_expression():
	liq = Liquid("{{a.a-b}}")
	assert liq.render(a = {'a-b':1}) == '1'

	liq = Liquid("{{a.a-b[0].x, b.c[1], b['c[1]']}}")
	assert liq.render(a = {'a-b':[{'x':2}]}, b={'c':[0, 3], 'c[1]': 'x'}) == "(2, 3, 'x')"

	liq = Liquid("{{a | @abs}}")
	assert liq.render(a = -1) == '1'

	liq = Liquid("{{a, b | *@at_least}}")
	assert liq.render(a = 4, b = 5) == '4'
	liq = Liquid("{{a, b | *@plus}}")
	assert liq.render(a = 4, b = 5) == '9'

	liq = Liquid("{{a | .a-b[0].x}}")
	assert liq.render(a = {'a-b':[{'x':2}]}) == "2"

def test_for():
	liq = Liquid("""
	{%- for i in x | range -%}
{{i}}
	{%- endfor -%}
""")
	assert liq.render(x = 10) == '0123456789'

	liq = Liquid("""
	{%- for i, a in x | enumerate -%}
{{i}}{{a}}
	{%- endfor -%}
""")
	assert liq.render(x = ['a','b','c']) == '0a1b2c'

	liq = Liquid("""
	{%- for k, v in x.items() -%}
{{k}}{{v}}
	{%- endfor -%}
""")
	assert liq.render(x = {'a':1,'b':2,'c':3}) == 'a1b2c3'

	liq = Liquid("""
	{%- for k, v in x.items() -%}
{%- if forloop.first -%}
First: {{k}},{{v}},{{forloop.index}},{{forloop.index0}},{{forloop.rindex}},{{forloop.rindex0}},{{forloop.length}}
{%- elif forloop.last -%}
Last: {{k}},{{v}},{{forloop.index}},{{forloop.index0}},{{forloop.rindex}},{{forloop.rindex0}},{{forloop.length}}
{%- endif -%}
	{%- endfor -%}
""")
	assert liq.render(x = {'a':1,'b':2,'c':3}) == 'First: a,1,1,0,3,2,3Last: c,3,3,2,1,0,3'

def test_comments():

	liq = Liquid("""{% mode compact %}
4
{% comment %}
1
2
{% endcomment %}
5
""")
	assert liq.render() == '4# 1\n# 25'

	liq = Liquid("""{% mode compact %}
4
{% comment // %}
1
2
{% endcomment %}
5
""")
	assert liq.render() == '4// 1\n// 25'

	liq = Liquid("""{% mode compact %}
4{# aa #}
{% comment /* */ %}
1
2
{% endcomment %}
5
""")
	assert liq.render() == '4/* 1 */\n/* 2 */5'

def test_raw():
	liq = Liquid("""{% mode compact %}
	{% raw %}
4{# aa #}
{% comment /* */ %}
1
2
{% endcomment %}
5
{% endraw %}
""")
	assert liq.render() == '4{# aa #}\n{% comment /* */ %}\n1\n2\n{% endcomment %}\n5'

def test_check_envs():
	with pytest.raises(LiquidWrongKeyWord):
		_check_envs({'true': 1})
	with pytest.raises(LiquidWrongKeyWord):
		_check_envs({'in': 1})
	with pytest.raises(LiquidWrongKeyWord):
		_check_envs({'from_file': 1}, ['from_file'])
	with pytest.raises(LiquidWrongKeyWord):
		_check_envs({'': 1})

def test_debug():

	Liquid.debug(False)
	assert not Liquid.debug()
	Liquid.debug(True)
	assert Liquid.debug()
	Liquid.debug(False)
	assert not Liquid.debug()

def test_init():
	with pytest.raises(ValueError):
		Liquid("a", from_file="b")


def test_render_error():
	liq = Liquid("""{% for i in a %}{{i}}{%endfor%}
1
2
3
4
5
6
""")
	with pytest.raises(LiquidRenderError):
		liq.render()
	Liquid.debug(True)
	with pytest.raises(LiquidRenderError):
		liq.render(b=1)
	Liquid.debug(False)


def test_syntax_error_single_include(debug, HERE):
	with pytest.raises(LiquidSyntaxError) as exc:
		Liquid("""1
2
3
4
5
6
7
{{% include {}/templates/include3.liq %}}
9
10
11
12
13
14
""".format(HERE))
	# liquid.exceptions.LiquidSyntaxError: Statement "for" expects format: "for var1, var2 in expr"
	#
	# Template call stacks:
	# ----------------------------------------------
	# File <LIQUID TEMPLATE SOURCE>
	#   > 8. {% include /.../liquidpy/tests/templates/include3.liq %}
	# File /.../liquidpy/tests/templates/include3.liq
	#     4.  4. comment
	#     5.  5. {% endcomment %}
	#     6.  6. {% for multi
	#     7.  7.    line, just
	#     8.  8.    to check if the
	#   > 9.  9.    line number is correct %}
	#     10. 10. {{ "I have" +
	#     11. 11.  "some other lines" }}
	#     12. 12. {% endfor %}
	stream = LiquidStream.from_string(str(exc.value))
	_, tag = stream.until(['Statement "for" expects format: "for var1, var2 in expr"'])
	assert bool(tag)
	_, tag = stream.until(['Template call stacks:'])
	assert bool(tag)
	_, tag = stream.until(['> 8. {% include'])
	assert bool(tag)
	_, tag = stream.until(['liquidpy/tests/templates/include3.liq'])
	assert bool(tag)
	_, tag = stream.until(['4.  4. comment'])
	assert bool(tag)
	_, tag = stream.until(['5.  5. {% endcomment %}'])
	assert bool(tag)
	_, tag = stream.until(['6.  6. {% for multi'])
	assert bool(tag)
	_, tag = stream.until(['7.  7.    line, just'])
	assert bool(tag)
	_, tag = stream.until(['8.  8.    to check if the'])
	assert bool(tag)
	_, tag = stream.until(['> 9.  9.    line number is correct %}'])
	assert bool(tag)
	_, tag = stream.until(['10. 10. {{ "I have" +'])
	assert bool(tag)
	_, tag = stream.until(['11. 11.  "some other lines" }}'])
	assert bool(tag)
	_, tag = stream.until(['12. 12. {% endfor %}'])
	assert bool(tag)

def test_syntax_error_multi_include(debug, HERE):
	with pytest.raises(LiquidSyntaxError) as exc:
		Liquid("{{% include {}/templates/include4.liq %}}".format(HERE))

	stream = LiquidStream.from_string(str(exc.value))
	_, tag = stream.until(['Statement "for" expects format: "for var1, var2 in expr"'])
	assert bool(tag)
	_, tag = stream.until(['Template call stacks:'])
	assert bool(tag)
	_, tag = stream.until(['File <LIQUID TEMPLATE SOURCE>'])
	assert bool(tag)
	_, tag = stream.until(['> 1. {% include'])
	assert bool(tag)
	_, tag = stream.until(['liquidpy/tests/templates/include4.liq'])
	assert bool(tag)
	_, tag = stream.until(['> 1. {% include include3.liq %}'])
	assert bool(tag)
	_, tag = stream.until(['liquidpy/tests/templates/include3.liq'])
	assert bool(tag)
	_, tag = stream.until(['4.  4. comment'])
	assert bool(tag)
	_, tag = stream.until(['5.  5. {% endcomment %}'])
	assert bool(tag)
	_, tag = stream.until(['6.  6. {% for multi'])
	assert bool(tag)
	_, tag = stream.until(['7.  7.    line, just'])
	assert bool(tag)
	_, tag = stream.until(['8.  8.    to check if the'])
	assert bool(tag)
	_, tag = stream.until(['> 9.  9.    line number is correct %}'])
	assert bool(tag)
	_, tag = stream.until(['10. 10. {{ "I have" +'])
	assert bool(tag)
	_, tag = stream.until(['11. 11.  "some other lines" }}'])
	assert bool(tag)
	_, tag = stream.until(['12. 12. {% endfor %}'])
	assert bool(tag)

def test_single_extends(debug, HERE):
	with pytest.raises(LiquidSyntaxError) as exc:
		Liquid("""1
2
3
4
5
6
7
{{% extends {}/templates/parent3.liq %}}
9
10
11
12
13
14
""".format(HERE))

	stream = LiquidStream.from_string(str(exc.value))

	# Unmatched end tag: 'endfor', expect 'endif'

	# Template call stacks:
	# ----------------------------------------------
	# File <LIQUID TEMPLATE SOURCE>
	#   > 8. {% extends /.../liquidpy/tests/templates/parent3.liq %}
	# File /.../liquidpy/tests/templates/parent3.liq
	# 	10. {% if true %}
	# 	11. 1
	# 	12. {%
	# 	13.
	# 	14.
	#   > 15. endfor %}
	# 	16. {% endcapture %}
	_, tag = stream.until(["Expecting a closing tag for '{%'"])
	assert bool(tag)
	_, tag = stream.until(["Template call stacks:"])
	assert bool(tag)
	_, tag = stream.until(["File <LIQUID TEMPLATE SOURCE>"])
	assert bool(tag)
	_, tag = stream.until(["> 8. {% extends"])
	assert bool(tag)
	_, tag = stream.until(["liquidpy/tests/templates/parent3.liq"])
	assert bool(tag)
	_, tag = stream.until(["9.  {% capture x %}"])
	assert bool(tag)
	_, tag = stream.until(["> 12. {%"])
	assert bool(tag)

def test_multi_extends(debug, HERE):
	with pytest.raises(LiquidSyntaxError) as exc:
		Liquid("{{% extends {}/templates/parent4.liq %}}".format(HERE))

	# Statement "for" expects format: "for var1, var2 in expr"
	#
	# Template call stacks:
	# ----------------------------------------------
	# File <LIQUID TEMPLATE SOURCE>
	#   > 1. {% extends /.../liquidpy/tests/templates/parent4.liq %}
	# File /.../liquidpy/tests/templates/parent4.liq
	#   > 6. {% include include3.liq %}
	# File /.../liquidpy/tests/templates/include3.liq
	#     4.  4. comment
	#     5.  5. {% endcomment %}
	#     6.  6. {% for multi
	#     7.  7.    line, just
	#     8.  8.    to check if the
	#   > 9.  9.    line number is correct %}
	#     10. 10. {{ "I have" +
	#     11. 11.  "some other lines" }}
	#     12. 12. {% endfor %}

	stream = LiquidStream.from_string(str(exc.value))
	_, tag = stream.until(['Statement "for" expects format: "for var1, var2 in expr"'])
	assert bool(tag)
	_, tag = stream.until(['Template call stacks:'])
	assert bool(tag)
	_, tag = stream.until(['File <LIQUID TEMPLATE SOURCE>'])
	assert bool(tag)
	_, tag = stream.until(['> 1. {% extends'])
	assert bool(tag)
	_, tag = stream.until(['liquidpy/tests/templates/parent4.liq'])
	assert bool(tag)
	_, tag = stream.until(['> 6. {% include include3.liq %}'])
	assert bool(tag)
	_, tag = stream.until(['liquidpy/tests/templates/include3.liq'])
	assert bool(tag)
	_, tag = stream.until(['4.  4. comment'])
	assert bool(tag)
	_, tag = stream.until(['> 9.  9.    line number is correct %}'])
	assert bool(tag)
	_, tag = stream.until(['12. 12. {% endfor %}'])
	assert bool(tag)

def test_include_extends(HERE, debug):

	liquid = Liquid("""
	{{%- mode compact %}}
	{{% extends {0}/templates/extends.liq %}}
	{{% block b2 %}}
	{{% include {0}/templates/include1.liq %}}
	{{{{x}}}}
	{{% endblock %}}
	""".format(HERE))

	assert liquid.render(x = 1) == 'empty blockabc10hij'

def test_cycle(debug):

	liquid = Liquid("""
{%- for i in range(10): -%}
{%- cycle 'a','b','c' -%}
{%- endfor -%}
""")
	liquid.render() == 'abcabcabca'

def test_nested_for(debug):
	liq = Liquid("""{% mode compact %}
{% for i in "a" %}
  {% for j in "c", "d" %}
    {% for k in "e", "f", "g" %}
    {{i}}-{{j}}-{{k}}-{{forloop.length}}/
	{% endfor %}
	{{forloop.length}}/
  {% endfor %}
  {{forloop.length}}/
{% endfor %}
""")
	assert liq.render() == 'a-c-e-3/a-c-f-3/a-c-g-3/2/a-d-e-3/a-d-f-3/a-d-g-3/2/1/'


def test_issue9(HERE, debug):
	liq = Liquid('{%% assign foo = "test" %%}{%% include %s/templates/include_issue9.liq %%}' % HERE)
	assert liq.render() == 'test\nAccented character "ì" for testing\ntest'

def test_unicode(HERE, debug):
	assert Liquid(from_file = '%s/templates/include_issue9.liq' % HERE).render(foo = 'bar') == 'bar\nAccented character "ì" for testing\nbar'