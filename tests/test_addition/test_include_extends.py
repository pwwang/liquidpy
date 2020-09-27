import pytest
from io import StringIO
from pathlib import Path
from liquid import *

HERE = Path(__file__).parent

def test_extends(caplog):
    liq = Liquid(str(HERE / 'templates' / 'curr.liquid'),
                 {'debug': True})
    assert liq.render() == '123'
    assert "Found <TagBlock('curr::b', compact 'none', line 3, column 10)>" in caplog.text

def test_extends_config():
    tpl = (HERE / 'templates' / 'curr2.liquid').open()
    liq = Liquid(tpl, dict(strict=False, mode='python'))
    assert liq.render() == 'abc'

def test_extends_error():
    with pytest.raises(LiquidSyntaxError):
        Liquid(HERE / 'templates' / 'error.liquid')

def test_must_be_level1():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% if 1 %}{% extends %}{% endif %}').render()

def test_mother_not_exists():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid(
            HERE / 'templates' / 'nomother.liquid'
    ).render()

def test_block_not_exists():
    with pytest.raises(LiquidRenderError) as exc:
        Liquid(
            HERE / 'templates' / 'noblock.liquid'
    ).render()

def test_include_extends():
    tpl = HERE / 'templates' / 'curr3.liquid'
    assert Liquid(tpl).render() == 'abcd'

def test_include_error():
    tpl = HERE / 'templates' / 'include_error.liquid'
    with pytest.raises(LiquidSyntaxError):
        Liquid(tpl)

def test_include_exception():
    tpl = f'''
    {{% config include_dir={HERE.resolve().joinpath('templates').as_posix()!r} %}}
    {{% include {HERE.resolve().joinpath('templates', 'include_render_error.liquid' )} %}}
    '''
    with pytest.raises(LiquidRenderError) as exc:
        Liquid(tpl, {'strict': False, 'debug': True}).render()
    assert '{{ 1 | nosuchfilter }}' in str(exc.value)
