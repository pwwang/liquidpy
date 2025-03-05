from liquid import Liquid
import pytest  # noqa


def test_ifelse(set_default_wild):
    tpl = """{{ a | ifelse: isinstance, (int, ),
               "plus", (1, ),
               "append", (".html", ) }}"""

    out = Liquid(tpl).render(a=1)
    assert out == "2"

    out = Liquid(tpl).render(a="a")
    assert out == "a.html"


def test_call(set_default_wild):
    tpl = """{{ int | call: "1" | plus: 1 }}"""

    out = Liquid(tpl).render()
    assert out == "2"


def test_map(set_default_wild):
    tpl = """{{ floor | map: x | list }}"""

    out = Liquid(tpl).render(x=[1.1, 2.2, 3.3])
    assert out == "[1, 2, 3]"
    out = Liquid(tpl).render(x=[])
    assert out == "[]"

    # liquid_map
    tpl = """{{ x | liquid_map: 'y' }}"""

    out = Liquid(tpl).render(x=[{"y": 1}, {"y": 2}, {"y": 3}])
    assert out == "[1, 2, 3]"
    out = Liquid(tpl).render(x=[])
    assert out == "[]"


def test_each(set_default_wild):
    tpl = """{{ x | each: plus, 1 }}"""

    out = Liquid(tpl).render(x=[1, 2, 3])
    assert out == "[2, 3, 4]"
    out = Liquid(tpl).render(x=[])
    assert out == "[]"
