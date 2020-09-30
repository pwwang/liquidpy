import pytest
from liquid import *

def test_register_filter():
    @filter_manager.register(mode='python')
    def incr(base, inc=1):
        return base + inc

    liq = Liquid('{{ 2 | incr}}', dict(mode='python'))
    assert liq.render() == '3'
    liq = Liquid('{{ 2 | incr:2}}', dict(mode='python'))
    assert liq.render() == '4'
    liq = Liquid('{{ 2 | incr:inc=3}}', dict(mode='python'))
    assert liq.render() == '5'

    liq = Liquid('{{ 2 | incr}}', dict(mode='standard'))
    with pytest.raises(LiquidRenderError):
        liq.render()

def test_unregister_filter():
    incr = filter_manager.unregister('incr', mode='python')
    assert incr(1) == 2

    with pytest.raises(LiquidFilterRegistryException):
        filter_manager.unregister('incr_no_such', mode='python')

def test_complex_filters():
    assert LiquidPython(
        '{{path | @__import__("pathlib").Path | getattr: "stem"}}'
    ).render(
        path='/a/b/cde.txt'
    ) == 'cde'

    assert LiquidPython(
        '{{path | @__import__("pathlib").Path | getattr: "stem" | getitem: 0}}'
    ).render(
        path='/a/b/cde.txt'
    ) == 'c'
