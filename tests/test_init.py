import pytest
import logging
from liquid import Liquid, _check_envs
from liquid.defaults import LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidWrongKeyWord, LiquidRenderError, LiquidSyntaxError

Liquid.debug(False)

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

def test_syntax_error():
	Liquid.debug(True)
	with pytest.raises(LiquidSyntaxError):
		Liquid("{%")
	Liquid.debug(False)
	with pytest.raises(LiquidSyntaxError):
		Liquid("{%")