from pathlib import Path
import pytest

from liquid import Liquid
from liquid.code import LiquidCode
from liquid.nodes import register_node, Node, parse_mixed, NodeVoid, NodeLiquidLiteral, NodeConfig, check_quotes, unquote
from liquid.exceptions import LiquidNodeAlreadyRegistered, LiquidSyntaxError, LiquidRenderError
HERE = Path(__file__).parent.resolve()

def test_register_node():
    with pytest.raises(LiquidNodeAlreadyRegistered):
        register_node('if', Node)



@pytest.mark.parametrize('mixed,expected', [
    ("`x | range`", "(range(x))")
])
def test_mixed(mixed, expected):
    assert parse_mixed(mixed, LiquidCode()) == expected

def test_mixed_error():
    with pytest.raises(LiquidSyntaxError):
        parse_mixed('`', LiquidCode())

    node = NodeVoid(name='void', attrs='', code=None, shared_code=LiquidCode())
    with pytest.raises(LiquidSyntaxError):
        node.try_mixed('`')

def test_empty_literal():
    code = LiquidCode()
    node = NodeLiquidLiteral(attrs='', code=code, shared_code=LiquidCode())
    assert node.parse_node() is None
    assert str(node.code) == ''

def test_empty_config():
    code = LiquidCode()
    node = NodeConfig(name='config', attrs='', code=code, shared_code=LiquidCode())
    with pytest.raises(LiquidSyntaxError):
        node.start()

    node.attrs = 'a'
    with pytest.raises(LiquidSyntaxError):
        node.start()

    node.attrs = 'a="1'
    with pytest.raises(LiquidSyntaxError):
        node.start()

def test_else_no_if_state():
    liq = Liquid("{% if False %}{%else%}1{%endif%}")
    assert liq.render() == '1'
    liq = Liquid("{% if False %}{%elseif true%}1{%endif%}")
    assert liq.render() == '1'

def test_python():
    liq = Liquid("{% python _liquid_ret_append('123') %}", liquid_loglevel='debug')
    assert liq.render() == '123'

    liq = Liquid("""
{%- python -%}
import math
_liquid_ret_append(math.ceil(1.1))
{%- endpython -%}""", liquid_loglevel='debug')
    assert liq.render() == '2'

def test_include():
    liq = Liquid(f"{{% include {HERE}/templates/include1.liq x=x %}}{{{{x}}}}")
    assert liq.render(x = 1) == '81'

    with pytest.raises(LiquidRenderError):
        Liquid(f"{{% include {HERE}/templates/include1.liq %}}{{{{x}}}}").render()

    with pytest.raises(LiquidSyntaxError):
        Liquid(f"{{% include {HERE}/templates/include1.liq , %}}").render()

    with pytest.raises(LiquidSyntaxError):
        Liquid(f"{{% include {HERE}/templates/include1.liq 9 %}}").render()

@pytest.mark.parametrize('value,expected', [
    ("", True),
    ("'", False),
    ("\"", False),
    ("a", True),
    ("'a\"", False),
    ("'a", False),
])
def test_check_quotes(value, expected):
    assert check_quotes(value) is expected

@pytest.mark.parametrize('value,expected', [
    ("", ""),
    ("''", ""),
    ("'a'", "a"),
    ("a", "a"),
])
def test_unquote(value, expected):
    assert unquote(value) == expected

def test_block():
    with pytest.raises(LiquidSyntaxError):
        liq = Liquid("{%block 1%}{% endblock %}")

def test_extends():
    with pytest.raises(LiquidSyntaxError):
        liq = Liquid("{% extends %}")

    with pytest.raises(LiquidSyntaxError) as exc:
        liq = Liquid(f"{{% extends {HERE}/templates/extends.liq %}}{{%extends {HERE}/templates/extends.liq%}}")
    assert "Only one 'extends' node allowed" in str(exc.value)

    # File not exists
    with pytest.raises(LiquidSyntaxError) as exc:
        liq = Liquid(f"{{% extends {HERE}/templates %}}")
