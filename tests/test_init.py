import pytest
import logging
from pathlib import Path
from liquid import Liquid, _shorten, _check_vars, LOGGER
from liquid.stream import LiquidStream
from liquid.code import LiquidCode
from liquid.defaults import LIQUID_LOGGER_NAME
from liquid.exceptions import LiquidRenderError, LiquidSyntaxError, LiquidNameError

@pytest.fixture
def HERE():
    return Path(__file__).parent.resolve()

@pytest.fixture
def debug():
    dbg = Liquid.debug()
    Liquid.debug(True)
    yield
    Liquid.debug(dbg)

def test_if_single():
    liq = Liquid("""
{% if a == 1 %}
abc{{b}}
{% endif %}
""")

    assert liq.render(a=1, b=2) == '\n\nabc2\n\n'

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
    liq = Liquid("{{a.a-b}}", liquid_loglevel='debug')
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
    {%- for i in `x | range` -%}
{{i}}
    {%- endfor -%}
""", liquid_loglevel='debug')
    assert liq.render(x = 10) == '0123456789'

    liq = Liquid("""
    {%- for i, a in `x | enumerate` -%}
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
""", liquid_loglevel='debug')
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

def test_init(HERE):
    with pytest.raises(FileNotFoundError):
        Liquid("a", liquid_from_file=True)

    tpl = HERE / 'templates' / 'parent5.liq'
    with tpl.open() as f:
        liq = Liquid(f, liquid_from_stream=True)

    assert liq.render() == "empty block"


def test_render_error():
    liq = Liquid("""{% for i in a %}{{i}}{%endfor%}
1
2
3
4
5
6
""", liquid_loglevel='info')
    with pytest.raises(LiquidRenderError):
        liq.render()

    liq = Liquid("""{% for i in a %}{{i}}{%endfor%}
1
2
3
4
5
6
""", liquid_loglevel='debug')
    with pytest.raises(LiquidRenderError):
        liq.render(b=1)


def test_syntax_error_single_include(HERE):
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
""".format(HERE), liquid_loglevel='debug')

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
    _, tag = stream.until(["'for' node expects format: 'for var1, var2 in expr'"])
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

def test_syntax_error_multi_include(HERE):
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid("{{% include {}/templates/include4.liq %}}".format(HERE),
                liquid_loglevel='debug')

    stream = LiquidStream.from_string(str(exc.value))
    _, tag = stream.until(["'for' node expects format: 'for var1, var2 in expr'"])
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
        liq = Liquid("""1
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
""".format(HERE), liquid_loglevel='debug')
    #print(exc.value)
    stream = LiquidStream.from_string(str(exc.value))

    # Unmatched end tag: 'endfor', expect 'endif'

    # Template call stacks:
    # ----------------------------------------------
    # File <LIQUID TEMPLATE SOURCE>
    #   > 8. {% extends /.../liquidpy/tests/templates/parent3.liq %}
    # File /.../liquidpy/tests/templates/parent3.liq
    # 	  10. {% if true %}
    # 	  11. 1
    # 	  12. {%
    # 	  13.
    # 	  14.
    #   > 15. endfor %}
    # 	  16. {% endcapture %}
    _, tag = stream.until(["Unclosed tag '{%'"])
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
        Liquid("{{% extends {}/templates/parent4.liq %}}".format(HERE),
             liquid_loglevel='debug')

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
    _, tag = stream.until(["'for' node expects format: 'for var1, var2 in expr'"])
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
    {{% include "{0}/templates/include1.liq" x %}}
    {{{{x}}}}
    {{% endblock %}}
    """.format(HERE), liquid_loglevel='debug')

    # variable now not allowed to be modified in included template
    assert liquid.render(x = 1) == 'empty blockabc81hij'
    #assert liquid.render(x = 1) == 'empty blockabc10hij'

    # make sure shared code only inserted once
    assert str(liquid.parser.shared_code).count("# TAGGED CODE: _liquid_dodots_function") == 1

    # compiled code:
    """
    def _liquid_render_function_47890221890024(_liquid_context):
      '''Main entrance function to render the template'''

      # TAGGED CODE: _liquid_dodots_function

      def _liquid_dodots_function(obj, dot):
        '''Allow dot operation for a.b and a["b"]'''
        try:
        return getattr(obj, dot)
        except (AttributeError, TypeError):
        return obj[dot]

      # ENDED TAGGED CODE


      # Rendered content
      _liquid_rendered = []
      _liquid_ret_append = _liquid_rendered.append
      _liquid_ret_extend = _liquid_rendered.extend

      # Environment and variables
      true = _liquid_context['true']
      false = _liquid_context['false']
      nil = _liquid_context['nil']
      _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']
      x = _liquid_context['x']

      _liquid_ret_append('empty block')
      _liquid_ret_append('abc')

      def _liquid_include_source_47890222238856(x):
        '''Build source from included file'''

        x = (x * 10)

      _liquid_include_source_47890222238856(x=x)
      _liquid_ret_append(x)
      _liquid_ret_append('hij')

      return ''.join(str(x) for x in _liquid_rendered)
    """

def test_include_extends_render_stacks(HERE):

    liquid = Liquid("""
    {{%- mode compact %}}
    {{% extends {0}/templates/extends.liq %}}
    {{% block b2 %}}
    {{% include "{0}/templates/include1.liq" x %}}
    {{{{x}}}}
    {{% endblock %}}
    """.format(HERE), liquid_loglevel='debug')
    # see if I have render stacks correct:
    with pytest.raises(LiquidRenderError) as exc:
        liquid.render(x = {}) # can't do {} * 10

    stream = LiquidStream.from_string(str(exc.value))
    _, tag = stream.until(["unsupported operand type(s) for *: 'dict' and 'int'"], wraps=[], quotes=[])
    assert bool(tag)
    _, tag = stream.until(["Template call stacks:"], wraps=[], quotes=[])
    assert bool(tag)
    _, tag = stream.until(["File <LIQUID TEMPLATE SOURCE>"])
    assert bool(tag)
    _, tag = stream.until(["> 5.     {% include"])
    assert bool(tag)
    _, tag = stream.until(["templates/include1.liq"], wraps = [], quotes = [])
    assert bool(tag)
    _, tag = stream.until(["> 1. {% assign"], wraps = [], quotes = [])
    assert bool(tag)
    _, tag = stream.until(["Compiled source"], wraps=[], quotes = [])
    assert bool(tag)
    _, tag = stream.until(["> 33."], wraps=[], quotes = [])
    assert bool(tag)

def test_include_extends_stacks(HERE):
    with pytest.raises(LiquidSyntaxError) as exc:
        liquid = Liquid("""
        {{%- mode compact %}}
        {{% extends {0}/templates/extends.liq %}}
        {{% block b2 %}}
        {{% include "{0}/templates/include4.liq" x %}}
        {{{{x}}}}
        {{% endblock %}}
        """.format(HERE), liquid_loglevel='debug')

    stream = LiquidStream.from_string(str(exc.value))
    _, tag = stream.until(["'for' node expects format: 'for var1, var2 in expr'"])
    assert bool(tag)
    _, tag = stream.until(["File <LIQUID TEMPLATE SOURCE>"])
    assert bool(tag)
    _, tag = stream.until(["> 5."])
    assert bool(tag)
    _, tag = stream.until(["File"])
    assert bool(tag)
    _, tag = stream.until(["> 1. {% include include3.liq %}"])
    assert bool(tag)
    _, tag = stream.until(["File"])
    assert bool(tag)
    _, tag = stream.until(["> 9."], wraps=[])
    assert bool(tag)

def test_extends_stacks():
    # if lineno is correct
    with pytest.raises(LiquidSyntaxError) as exc:
        liq = Liquid("""
                    {% extends x %}
                    {% if 1 %}
                    {% endif %}
                    """, liquid_loglevel='debug')
    assert '> 2.' in str(exc.value)

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
""", liquid_loglevel='debug')
    assert liq.render() == 'a-c-e-3/a-c-f-3/a-c-g-3/2/a-d-e-3/a-d-f-3/a-d-g-3/2/1/'


def test_issue9(HERE, debug):
    liq = Liquid('{%% assign foo = "test" %%}{%% include %s/templates/include_issue9.liq %%}' % HERE, liquid_loglevel='debug')
    assert liq.render() == 'test\nAccented character "ì" for testing\ntest'


def test_unicode(HERE, debug):
    assert Liquid(from_file = '%s/templates/include_issue9.liq' % HERE).render(foo = 'bar') == 'bar\nAccented character "ì" for testing\nbar'


def test_unicode_string(debug):
    template = """{{foo}}
Accented character "ì" for testing
{{foo}}"""
    assert Liquid(template).render(foo = 'bar') == 'bar\nAccented character "ì" for testing\nbar'

@pytest.mark.parametrize('string,length,expected', [
    ('a', 1, 'a'),
    ('1234567890123456', 10, '123 ... 456')
])
def test_shorten(string, length, expected):
    _shorten(string, length) == expected

@pytest.mark.parametrize('vars, expected', [
    ({'a':1}, True),
    ({'1a':1}, False),
])
def test_check_vars(vars, expected):
    if not expected:
        with pytest.raises(LiquidNameError):
            _check_vars(vars)
    else:
        assert _check_vars(vars) is None

def test_include_config_switching(HERE):
    # test config switches in different parsers/files
    master = f"""
    {{% config mode=loose, loglevel=debug %}}
    {{{{1}}}}
    {{% include {HERE}/templates/parent5.liq %}}{{# in compact mode, loglevel=info #}}
    {{{{2}}}}"""
    liq = Liquid(master)
    assert LOGGER.level == 10
    #                                                     we should go back
    #                                                     to loose mode
    assert liq.render() == '\n    \n    1\n    empty block\n    2'
    # loglevel should not be changed
    assert LOGGER.level == 10

def test_extends_config_switching(HERE):
    # test config switches in different parsers/files
    master = f"""
    {{% config mode=loose, loglevel=debug %}}
    {{{{1}}}}
    {{% extends {HERE}/templates/parent5.liq %}}{{# in compact mode, loglevel=info #}}
    {{% block b1 %}}
    {{{{2}}}}
    {{% endblock %}}"""
    liq = Liquid(master)
    assert LOGGER.level == 10
    #                                                     we should go back
    #                                                     to loose mode
    assert liq.render() == 'empty block\n    2\n    '
    # loglevel should not be changed
    assert LOGGER.level == 10

