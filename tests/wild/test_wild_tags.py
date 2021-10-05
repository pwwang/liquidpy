
import pytest

from liquid import Liquid
from jinja2.exceptions import TemplateSyntaxError

def test_python_inline(set_default_wild):
    tpl = """
    {% python a = 1 %}{{a}}
    """
    assert Liquid(tpl).render().strip() == "1"

def test_python_block(set_default_wild):
    tpl = """
    {% python %}
    a = 1
    {% endpython %}
    {{a}}
    """
    assert Liquid(tpl).render().strip() == "1"

def test_import_block(set_default_wild):
    tpl = """
    {% import_ os %}
    {{os.path.join("a", "b")}}
    """
    assert Liquid(tpl).render().strip() == "a/b"

def test_from_block(set_default_wild):
    tpl = """
    {% from_ os import path %}
    {{path.join("a", "b")}}
    """
    assert Liquid(tpl).render().strip() == "a/b"

def test_addfilter(set_default_wild):
    tpl = """
    {% addfilter path_join %}
    import os
    path_join = os.path.join
    {% endaddfilter %}
    {{"a" | path_join: "b"}}
    """
    assert Liquid(tpl).render().strip() == "a/b"

def test_addfilter_err(set_default_wild):
    tpl = """
    {% addfilter path_join %}
    x = 1
    {% endaddfilter %}
    """
    with pytest.raises(TemplateSyntaxError, match="No such filter defined"):
        Liquid(tpl)
