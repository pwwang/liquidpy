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
