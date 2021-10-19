from re import template
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


def test_markdownify(set_default_jekyll):
    assert Liquid("{{ '# a' | markdownify }}").render() == "<h1>a</h1>"


@pytest.mark.parametrize(
    "sen,mode,out",
    [
        ('Hello world!', None, 2),
        ('hello world and taoky strong!', "cjk", 5),
        ('hello world and taoky strong!', "auto", 5),
        ('こんにちは、世界！안녕하세요 세상!', "cjk", 17),
        ('こんにちは、世界！안녕하세요 세상!', "auto", 17),
        ('你好hello世界world', None, 1),
        ('你好hello世界world', "cjk", 6),
        ('你好hello世界world', "auto", 6),
    ]
)
def test_number_of_words(sen,mode,out,set_default_jekyll):
    if mode is None:
        template = f"{{{{ {sen!r} | number_of_words }}}}"
    else:
        template = f"{{{{ {sen!r} | number_of_words: {mode!r} }}}}"

    assert Liquid(template).render() == str(out)


def test_sort_error(set_default_jekyll):
    template = Liquid("{{ x | sort }}")
    with pytest.raises(ValueError):
        template.render(x=None)

    template = Liquid("{{ x | sort: p, n }}")
    with pytest.raises(ValueError):
        template.render(x=[], p=None, n=None)


@pytest.mark.parametrize(
    "array, prop, none_pos, out",
    [
        ([10, 2], None, "first", [10, 2]),
        ([None, 10, 2], None, "first", [None, 10, 2]),
        ([None, 10, 2], None, "last", [10, 2, None]),
        (["FOO", "Foo", "foo"], None, "first", ["foo", "Foo", "FOO"]),
        # acts differently then ruby
        # (["_foo", "foo", "foo_"], None, "first", ["foo_", "_foo", "foo"]),
        (["_foo", "foo", "foo_"], None, "first", ["foo_", "foo", "_foo"]),
        # (["ВУЗ", "Вуз", "вуз"], None, "first", ["Вуз", "вуз", "ВУЗ"]),
        (["ВУЗ", "Вуз", "вуз"], None, "first", ["вуз", "Вуз", "ВУЗ"]),
        (["_вуз", "вуз", "вуз_"], None, "first", ["вуз_", "вуз", "_вуз"]),
        (["אלף" ,"בית"], None, "first", ["בית" ,"אלף"]),
        (
            [{ "a": 1 }, { "a": 2 }, { "a": 3 }, { "a": 4 }],
            "a",
            "first",
            [{ "a": 4 }, { "a": 3 }, { "a": 2 }, { "a": 1 }],
        ),
        (
            [{ "a": ".5" }, { "a": "0.65" }, { "a": "10" }],
            "a",
            "first",
            [{ "a": "10" }, { "a": "0.65" }, { "a": ".5" }],
        ),
        (
            [{ "a": ".5" }, { "a": "0.6" }, { "a": "twelve" }],
            "a",
            "first",
            [{ "a": "twelve" }, { "a": "0.6" }, { "a": ".5" }],
        ),
        (
            [{ "a": "1" }, { "a": "1abc" }, { "a": "20" }],
            "a",
            "first",
            [{ "a": "20" }, { "a": "1abc" }, { "a": "1" }],
        ),
        (
            [{ "a": 2 }, { "b": 1 }, { "a": 1 }],
            "a",
            "first",
            [{ "b": 1 }, { "a": 2 }, { "a": 1 }],
        ),
        (
            [{ "a": 2 }, { "b": 1 }, { "a": 1 }],
            "a",
            "last",
            [{ "a": 2 }, { "a": 1 }, { "b": 1 }],
        ),
        (
            [{ "a": { "b": 1 } }, { "a": { "b": 2 } }, { "a": { "b": 3 } }],
            "a.b",
            "first",
            [{ "a": { "b": 3 } }, { "a": { "b": 2 } }, { "a": { "b": 1 } }],
        ),
    ]
)
def test_sort(array, prop, none_pos, out, set_default_jekyll):
    assert Liquid("{{x | sort: p, n}}").render(
        x=array,
        p=prop,
        n=none_pos
    ) == str(out)
