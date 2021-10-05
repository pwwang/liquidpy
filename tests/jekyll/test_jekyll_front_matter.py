import pytest
from liquid import Liquid

def test_front_matter_toml(set_default_jekyll):
    tpl = """+++
a = 1
+++

{{page.a}}
"""
    assert Liquid(tpl, front_matter_lang="toml").render().strip() == "1"

def test_front_matter_json(set_default_jekyll):
    tpl = """{
"a": 1
}

{{page.a}}
"""
    assert Liquid(tpl, front_matter_lang="json").render().strip() == "1"
