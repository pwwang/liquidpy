import pytest
from diot import Diot
from liquid import *

def test_register_tag():

    from liquid.python.tags import Tag

    @tag_manager.register('print,echo', mode='python')
    class TagEcho(Tag):
        VOID = True
        START = 'var'

        def _render(self, local_vars, global_vars):
            return str(self.parsed)

    liq = Liquid('{% echo abc %}', {'mode': 'python'})
    assert liq.render() == 'abc'

    liq = Liquid('{% print abc %}', {'mode': 'python'})
    assert liq.render() == 'abc'

    assert tag_manager.unregister('echo', mode='python') is TagEcho
    with pytest.raises(LiquidTagRegistryException):
        tag_manager.unregister('print')

def test_op():
    assert Liquid('{% if 1 in (1,) %}1{% endif %}',
                  {'mode': 'python'}).render() == '1'
    assert Liquid('{% unless 1 not in (1,) %}1{% endunless %}',
                  {'mode': 'python'}).render() == '1'
    assert Liquid('{% unless 1 is 1 %}1{% else %}2{% endunless %}',
                  {'mode': 'python'}).render() == '2'
    assert Liquid('{% unless 1 is not 1 %}1{% else %}2{% endunless %}',
                  {'mode': 'python'}).render() == '1'

def test_COMMENT():
    assert Liquid('{# whatever #}', dict(mode='python')).render() == ''

def test_assign():
    # test some grammars here
    assert Liquid('{% assign x = 1 %}{{x}}', {'mode': 'python'}).render() == '1'
    assert Liquid('''
        {% assign x = y[0] %}{{x}}
    ''', {'mode': 'python'}).render(
        y = [1,2,3]
    ).strip() == '1'
    assert Liquid('''
        {% assign x = y[0:] %}{{x[0]}}
    ''', {'mode': 'python'}).render(
        y = [1,2,3]
    ).strip() == '1'
    assert Liquid('''
        {% assign x = [1,2,3] %}{{x[0]}}
    ''', {'mode': 'python'}).render().strip() == '1'
    assert Liquid('''
        {% assign x = [1] %}{{x[0]}}
    ''', {'mode': 'python'}).render().strip() == '1'
    assert Liquid('''
        {% assign x = (1,2,3) %}{{x[0]}}
    ''', {'mode': 'python'}).render().strip() == '1'
    assert Liquid('''
        {% assign x = {1,2,3} %}{{list(x)[0]}}
    ''', {'mode': 'python'}).render().strip() == '1'
    assert Liquid('''
        {% assign x = {1,2,3} %}{{ x | len }}
    ''', {'mode': 'python'}).render().strip() == '3'
    assert Liquid('''
        {% assign x = {'a':1, 'b':2, 'c':3} %}{{x['a']}}
    ''', {'mode': 'python'}).render().strip() == '1'

def test_assign_expr():
    liq = Liquid('''
        {% assign x = a - 1 %}{{x}}
    ''', {'mode': 'python'}).render(a=2)
    assert liq.strip() == '1'

    liq = Liquid('''
        {% assign x = a ** 3 %}{{x}}
    ''', {'mode': 'python'}).render(a=2)
    assert liq.strip() == '8'

def test_if_else():
    assert Liquid('''
    {% if False %}1{%else %}2{%endif %}
    ''', {'mode': 'python'}).render().strip() == '2'
    assert Liquid('''
    {% if False %}1{%else if False %}2{% else%}3{%endif %}
    ''', {'mode': 'python', 'debug': True}).render().strip() == '3'

def test_output():
    assert Liquid(
        '{{[1,2][1 if True else 2]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2,3][1 if False else 2]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{[1,2,3][0 or 2]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{[1,2,3][0 or 0]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][1 and 0]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][1 and 2]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{[1,2,3][(not True) or 2]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{a.a}}', {'mode': 'python'}
    ).render(a=Diot(a=1)) == '1'
    assert Liquid(
        '{{a.a}}', {'mode': 'python'}
    ).render(a={'a': 1}) == '1'
    with pytest.raises(LiquidRenderError):
        assert Liquid(
            '{{a.a}}', {'mode': 'python'}
        ).render(a={})

    with pytest.raises(LiquidRenderError):
        Liquid('{{1 | no_such_filter}}', {'mode': 'python'}).render()

def test_expr():
    assert Liquid(
        '{{[1,2][1 || 1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2][1 & 1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2][1 ^ 1]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][1 << 1]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{[1,2,3][1 >> 1]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][1 + 1]}}', {'mode': 'python'}
    ).render() == '3'
    assert Liquid(
        '{{[1,2,3][1 - 1]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][int(1 / 1)]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2,3][1 // 1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2,3][1 % 1]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][1 * 1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2,3][1 ** 1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{[1,2,3][~-1]}}', {'mode': 'python'}
    ).render() == '1'
    assert Liquid(
        '{{[1,2,3][+1]}}', {'mode': 'python'}
    ).render() == '2'
    assert Liquid(
        '{{list()}}', {'mode': 'python'}
    ).render() == '[]'
    assert Liquid(
        '{{a > 0}}', {'mode': 'python'}
    ).render(a=1) == 'True'

def test_collections():
    assert Liquid(
        '{{()}}', {'mode': 'python'}
    ).render() == '()'
    assert Liquid(
        '{{[]}}', {'mode': 'python'}
    ).render() == '[]'
    assert Liquid(
        '{{ {} }}', {'mode': 'python'}
    ).render() == '{}'

def test_else_following():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{%if False%}{%else%}{%else%}{%endif%}',
               {'mode': 'python'})
    assert 'No tags allowed after' in str(exc.value)

def test_elif():

    assert Liquid('{% if a %}a{% elif b %}b{% endif %}',
                  {'mode': 'python'}).render(a=1, b=0) == 'a'
    assert Liquid('{% if a %}a{% elif b %}b{% endif %}',
                  {'mode': 'python'}).render(a=0, b=1) == 'b'
    assert Liquid('{% if a %}a{% elsif b %}b{% endif %}',
                  {'mode': 'python'}).render(a=1, b=0) == 'a'
    assert Liquid('{% if a %}a{% elsif b %}b{% endif %}',
                  {'mode': 'python'}).render(a=0, b=1) == 'b'


def test_for():

    assert Liquid('{% for i in range(3) %}{{i}}{% endfor %}',
                  {'mode': 'python'}).render() == '012'

    assert Liquid('''{% for i in range(3) -%}
        {% if i == 0 %}{% continue %}{% endif %}{{i}}
        {%- endfor -%}
    ''', {'mode': 'python'}).render() == '12'

    assert Liquid('''{% for i in range(3) -%}
        {% if i == 1 %}{% break %}{% endif %}{{i}}
        {%- endfor -%}
    ''', {'mode': 'python'}).render() == '0'

    assert Liquid('''{% for i in range(3) -%}
        {{i}}
        {%- else -%}x
        {%- endfor -%}
    ''', {'mode': 'python'}).render() == '012x'

    assert Liquid('''{% for i in range(3) -%}
        {{i}}{% break %}
        {%- else -%}x
        {%- endfor -%}
    ''', {'mode': 'python'}).render() == '0'

    assert Liquid('''{% for i in 3 | range -%}
        {{i}}{% break %}
        {%- else -%}x
        {%- endfor -%}
    ''', {'mode': 'python'}).render() == '0'

    assert Liquid('''{% for key, val in d.items() -%}
        {{key}}-{{val}}{% break %}
        {%- endfor -%}
    ''', {'mode': 'python'}, d={'a': 1}).render().strip() == 'a-1'

def test_while():

    assert Liquid('''
    {% assign x = 2 %}
    {% while x > 0 -%}
        {{- x -}}
        {%assign x = x - 1 -%}
    {% else -%}9
    {%- endwhile -%}
    ''', {'mode': 'python'}).render().strip() == '219'

    assert Liquid('''
    {% assign x = 2 %}
    {% while x > 0 -%}
        {{- x -}}
        {% if x == 1 %}{%break %}{%endif -%}
        {%assign x = x - 1 -%}
    {% else -%}9
    {%- endwhile -%}
    ''', {'mode': 'python'}).render().strip() == '21'

def test_lambda():
    tpl = """
    {% assign x = lambda a: a+1 %}
    {{1 | x}}
    """
    assert Liquid(tpl, {'mode': 'python'}).render().strip() == '2'

    tpl = """
    {% assign x = lambda a, b, c=1: a+b+c %}
    {{x(1,2,3)}}
    """
    assert Liquid(tpl, {'mode': 'python'}).render().strip() == '6'


    tpl = """
    {% assign x = lambda a, b, c=1: a+b+c %}
    {{x(1,2,3, c=1)}}
    """
    with pytest.raises(LiquidRenderError) as exc:
        assert Liquid(tpl, {'mode': 'python'}).render()
    assert 'got multiple values' in str(exc.value)

    tpl = """
    {{1 | lambda a: a+1}}
    """
    assert Liquid(tpl, {'mode': 'python'}).render().strip() == '2'

def test_filter_arg_position():
    tpl = """
    {% assign f = lambda a, b: a+b %}
    {{ x | f: 1, _ }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=2).strip() == '3'

def test_ternary_filter():
    tpl = """
    {{ x | ? plus: 1 ! minus: 1}}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=2).strip() == '3'
    assert Liquid(tpl, {'mode': 'python'}).render(x=0).strip() == '-1'

    tpl = """
    {{ x | plus: 1 ? plus: 1 ! minus: 1}}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=2).strip() == '3'
    assert Liquid(tpl, {'mode': 'python'}).render(x=-1).strip() == '-2'

    tpl = """
    {{ x | ? plus: 1 ! }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=2).strip() == '3'
    assert Liquid(tpl, {'mode': 'python'}).render(x=0).strip() == '0'

    tpl = """
    {{ x | ?! plus: 1 }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=2).strip() == '2'
    assert Liquid(tpl, {'mode': 'python'}).render(x=0).strip() == '1'

def test_dot_filter():

    tpl = """
    {{ x | .__len__ }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x="abc").strip() == '3'
    tpl = """
    {{ x | .join: ['a', 'b', 'c'] }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(x=",").strip() == 'a,b,c'

def test_subscript_filter():

    tpl = """
    {{ x | ['a']: 1 }}
    """
    assert Liquid(tpl, {'mode': 'python'}).render(
        x={'a': lambda a: a+2}
    ).strip() == '3'

def test_dot_subscript_filter_error():
    tpl = """
    {{ x | .__len__ }}
    """
    with pytest.raises(LiquidRenderError) as exc:
        Liquid(tpl, {'mode': 'python'}).render(x=object())
    assert 'No such filter' in str(exc.value)
    tpl = """
    {{ x | ['a'] }}
    """
    with pytest.raises(LiquidRenderError) as exc:
        Liquid(tpl, {'mode': 'python'}).render(x=object())
    assert 'No such filter' in str(exc.value)

def test_complex_start_keyword_filters():
    with pytest.raises(LiquidRenderError) as exc:
        Liquid('{{ 1 | @a.b }}', {'mode': 'python'}).render()
    assert 'No such filter' in str(exc.value)

    @filter_manager.register(mode='python')
    def addx(a, b):
        return a + b

    tpl = '''{{ {'a':1, 'b':2} | **addx}}'''
    assert Liquid(tpl, {'mode': 'python'}).render() == '3'

def test_no_emptydrop():
    assert Liquid("{{[] | sort}}", {'mode': 'python'}).render() == '[]'
    assert Liquid("{{[3,2,1] | sort}}",
                  {'mode': 'python'}).render() == '[1, 2, 3]'

def test_python_void():
    assert Liquid("{% python x = a %}{{x}}",
                  {'mode': 'python', 'strict': False}).render(a=1) == '1'

def test_python_block():
    Liquid("""
    {% python %}
    {% if x %}
    a = 1
    {% else %}
    a = 2
    {% endif %}
    {% endpython %}{{a}}
    """, {'mode': 'python', 'strict': False}).render(x=True).strip() == '1'

def test_import():
    tpl = """
    {% import os %}
    {{ os.path.join("a", "b") }}
    """

    assert Liquid(tpl,
                  {'mode': 'python', 'strict': False}).render().strip() == 'a/b'
    tpl = """
    {% import os as ooss %}
    {{ ooss.path.join("a", "b") }}
    """

    assert Liquid(tpl,
                  {'mode': 'python', 'strict': False}).render().strip() == 'a/b'

def test_from():
    tpl = """
    {% from os import path %}
    {{ path.join("a", "b") }}
    """

    assert Liquid(tpl,
                  {'mode': 'python', 'strict': False}).render().strip() == 'a/b'
    tpl = """
    {% from os import path as path2 %}
    {{ ("a", "b") | *@path2.join }}
    """

    assert Liquid(tpl,
                  {'mode': 'python', 'strict': False}).render().strip() == 'a/b'


