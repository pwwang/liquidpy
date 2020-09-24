import pytest
from diot import Diot
from liquid import *

def test_register_tag():

    from liquid.python.tags import Tag
    from liquid.python.tags.transformer import TagTransformer

    @tag_manager.register('print', mode='python')
    class TagEcho(Tag):
        VOID = True
        START = 'varname'

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
        '{{[1,2][1 | 1]}}', {'mode': 'python'}
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
