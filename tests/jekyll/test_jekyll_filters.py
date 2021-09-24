import pytest
from liquid import Liquid


def test_relative_url(set_default_jekyll):
    with pytest.raises(ValueError, match="Global variables"):
        Liquid('{{"b/c" | relative_url}}').render()

    out = Liquid(
        '{{"b/c" | relative_url}}', globals={"site": {"baseurl": "/a"}}
    ).render()
    assert out == "/a/b/c"


def test_find(set_default_jekyll):
    liq = Liquid('{{ obj | find: "a", 1 }}')
    out = liq.render(
        obj=[
            {"a": 1, "b": 2},
            {"a": 2, "b": 4},
        ]
    )
    assert out == "{'a': 1, 'b': 2}"

    out = liq.render(obj=[])
    assert out == "None"

    out = liq.render(obj=[{}])
    assert out == "None"


def test_normalize_whitespace(set_default_jekyll):
    assert Liquid('{{"a    b" | normalize_whitespace}}').render() == "a b"


def test_sample(set_default_jekyll):
    assert Liquid("{{arr | sample | first}}").render(arr=[1, 2, 3], n=1) in [
        "1",
        "2",
        "3",
    ]
