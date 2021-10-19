"""Tests grabbed from:
https://shopify.github.io/liquid/filters/abs/
"""
import pytest
from datetime import datetime

from liquid import Liquid


@pytest.mark.parametrize(
    "base,filter,result",
    [
        (-17, "abs", 17),
        ("/my/fancy/url", 'append: ".html"', "/my/fancy/url.html"),
        # (1.2, 'round', 1),
        # (2.7, 'round', 3),
        (1.2, "round", 1.0),
        (2.7, "round", 3.0),
        (183.357, "round: 2", 183.36),
        (3, "times: 2", 6),
        (24, "times: 7", 168),
        (183.357, "times: 12", 2200.284),
        (4, "plus: 2", 6),
        (16, "plus: 4", 20),
        (183.357, "plus: 12", 195.357),
        (4, "minus: 2", 2),
        (16, "minus: 4", 12),
        (183.357, "minus: 12", 171.357),
        (3, "modulo: 2", 1),
        (24, "modulo: 7", 3),
        (183.357, "modulo: 12 | round: 3", 3.357),
        (4, "at_least: 5", 5),
        (4, "at_least: 3", 4),
        (4, "at_most: 5", 4),
        (4, "at_most: 3", 3),
        ("title", "capitalize", "Title"),
        ("my great title", "capitalize", "My great title"),
        (1.2, "ceil", 2),
        (1.2, "floor", 1),
        (2.0, "ceil", 2),
        (2.0, "floor", 2),
        (183.357, "ceil", 184),
        (183.357, "floor", 183),
        ("3.5", "ceil", 4),
        ("3.5", "floor", 3),
        ("Fri, Jul 17, 15", 'date: "%a, %b %d, %y"', "Fri, Jul 17, 15"),
        ("Fri, Jul 17, 15", 'date: "%Y"', "2015"),
        ("now", 'date: "%Y-%m-%d %H"', datetime.now().strftime("%Y-%m-%d %H")),
        ("today", 'date: "%Y-%m-%d"', datetime.today().strftime("%Y-%m-%d")),
        ("", "default: 2.99", 2.99),
        (4.99, "default: 2.99", 4.99),
        (0, "default: 2.99", 0),
        (False, "default: True, allow_false: True", "False"),
        (16, "divided_by: 4", 4),
        (5, "divided_by: 3", 1),
        (20, "divided_by: 7", 2),
        (20, "divided_by: 7.0 | round: 2", 2.86),
        (
            "apples, oranges, and bananas",
            'prepend: "Some fruit: "',
            "Some fruit: apples, oranges, and bananas",
        ),
        ("Parker Moore", "downcase", "parker moore"),
        ("apple", "downcase", "apple"),
        ("Parker Moore", "upcase", "PARKER MOORE"),
        ("apple", "upcase", "APPLE"),
        (
            "Have you read 'James & the Giant Peach'?",
            "escape",
            "Have you read &#x27;James &amp; the Giant Peach&#x27;?",
        ),
        ("Tetsuro Takara", "escape", "Tetsuro Takara"),
        ("1 < 2 & 3", "escape_once", "1 &lt; 2 &amp; 3"),
        ("1 &lt; 2 &amp; 3", "escape_once", "1 &lt; 2 &amp; 3"),
        ("Ground control to Major Tom.", 'split: " " | first', "Ground"),
        (
            "John, Paul, George, Ringo",
            'split: ", " | join: " and "',
            "John and Paul and George and Ringo",
        ),
        ("Ground control to Major Tom.", 'split: " " | last', "Tom."),
        (
            "          So much room for activities!          ",
            "lstrip",
            "So much room for activities!          ",
        ),
        (
            "          So much room for activities!          ",
            "rstrip",
            "          So much room for activities!",
        ),
        (
            "          So much room for activities!          ",
            "strip",
            "So much room for activities!",
        ),
        (
            "I strained to see the train through the rain",
            'remove: "rain"',
            "I sted to see the t through the ",
        ),
        (
            "I strained to see the train through the rain",
            'remove_first: "rain"',
            "I sted to see the train through the rain",
        ),
        (
            "Take my protein pills and put my helmet on",
            'replace: "my", "your"',
            "Take your protein pills and put your helmet on",
        ),
        (
            "Take my protein pills and put my helmet on",
            'replace_first: "my", "your"',
            "Take your protein pills and put my helmet on",
        ),
        (
            "apples, oranges, peaches, plums",
            'split: ", " | reverse | join: ", "',
            "plums, peaches, oranges, apples",
        ),
        (
            "Ground control to Major Tom.",
            'split: "" | reverse | join: ""',
            ".moT rojaM ot lortnoc dnuorG",
        ),
        ("Ground control to Major Tom.", "size", 28),
        ("Ground control to Major Tom.", 'split: " " | size', 5),
        ("%27Stop%21%27+said+Fred", "url_decode", "'Stop!'+said+Fred"),
        ("john@liquid.com", "url_encode", "john%40liquid.com"),
        ("Tetsuro Takara", "url_encode", "Tetsuro+Takara"),
        ("Liquid", "slice: 0", "L"),
        ("Liquid", "slice: 2", "q"),
        ("Liquid", "slice: 2, 5", "quid"),
        ("Liquid", "slice: -3, 2", "ui"),
        (
            "zebra, octopus, giraffe, Sally Snake",
            'split: ", " | sort | join: ", "',
            "Sally Snake, giraffe, octopus, zebra",
        ),
        (
            "zebra, octopus, giraffe, Sally Snake",
            'split: ", " | sort_natural | join: ", "',
            "giraffe, octopus, Sally Snake, zebra",
        ),
        (
            "John, Paul, George, Ringo",
            'split: ", "',
            ["John", "Paul", "George", "Ringo"],
        ),
        (
            "Have <em>you</em> read <strong>Ulysses</strong>?",
            "strip_html",
            "Have you read Ulysses?",
        ),
        (
            "Ground control to Major Tom.",
            "truncate: 20",
            "Ground control to...",
        ),
        (
            "Ground control to Major Tom.",
            "truncate: 120",
            "Ground control to Major Tom.",
        ),
        (
            "Ground control to Major Tom.",
            'truncate: 25, ", and so on"',
            "Ground control, and so on",
        ),
        (
            "Ground control to Major Tom.",
            'truncate: 20, ""',
            "Ground control to Ma",
        ),
        (
            "Ground control to Major Tom.",
            "truncatewords: 3",
            "Ground control to...",
        ),
        (
            "Ground control to Major Tom.",
            "truncatewords: 30",
            "Ground control to Major Tom.",
        ),
        (
            "Ground control to Major Tom.",
            'truncatewords: 3, "--"',
            "Ground control to--",
        ),
        (
            "Ground control to Major Tom.",
            'truncatewords: 3, ""',
            "Ground control to",
        ),
        (
            "ants, bugs, bees, bugs, ants",
            'split: ", " | uniq | join: ", "',
            "ants, bugs, bees",
        ),
    ],
)
def test_single_filter(base, filter, result, set_default_standard):
    tpl = f"{{{{ {base!r} | {filter} }}}}"
    assert Liquid(tpl).render() == str(result)


def test_newline_filters(set_default_standard):
    assert Liquid("{{ x | newline_to_br }}").render(x="apple\nwatch") == (
        "apple<br />watch"
    )
    assert Liquid("{{ x | strip_newlines }}").render(x="apple\nwatch") == (
        "applewatch"
    )


def test_filter_var_args(set_default_standard):
    tpl = """
    {% assign filename = "/index.html" %}
    {{ "website.com" | append: filename }}
    """
    assert Liquid(tpl).render().strip() == "website.com/index.html"


def test_compact(set_default_standard):
    tpl = """
    {%- assign site_categories = site.pages | map: "category" -%}
    {%- for category in site_categories %}
    - {{ category -}}.
    {%- endfor %}
    """
    rendered = Liquid(tpl).render(
        site={
            "pages": [
                {"category": "business"},
                {"category": "celebrities"},
                {"category": ""},
                {"category": "lifestyle"},
                {"category": "sports"},
                {"category": ""},
                {"category": "technology"},
            ]
        }
    )
    assert (
        rendered
        == """
    - business.
    - celebrities.
    - .
    - lifestyle.
    - sports.
    - .
    - technology.
    """
    )

    tpl = """
    {%- assign site_categories = site.pages | map: "category" | compact -%}
    {%- for category in site_categories %}
    - {{ category }}.
    {%- endfor %}
    """
    rendered = Liquid(tpl).render(
        site={
            "pages": [
                {"category": "business"},
                {"category": "celebrities"},
                {"category": ""},
                {"category": "lifestyle"},
                {"category": "sports"},
                {"category": ""},
                {"category": "technology"},
            ]
        }
    )
    assert (
        rendered
        == """
    - business.
    - celebrities.
    - lifestyle.
    - sports.
    - technology.
    """
    )


def test_concat(set_default_standard):
    tpl = """
    {%- assign fruits = "apples, oranges, peaches" | split: ", " -%}
    {%- assign vegetables = "carrots, turnips, potatoes" | split: ", " -%}
    {%- assign everything = fruits | concat: vegetables -%}
    {%- for item in everything %}
    - {{ item }}
    {%- endfor %}
    """
    assert (
        Liquid(tpl).render()
        == """
    - apples
    - oranges
    - peaches
    - carrots
    - turnips
    - potatoes
    """
    )

    tpl = """
    {%- assign fruits = "apples, oranges, peaches" | split: ", " -%}
    {%- assign furniture = "chairs, tables, shelves" | split: ", " -%}
    {%- assign vegetables = "carrots, turnips, potatoes" | split: ", " -%}
    {%- assign everything = fruits | concat: vegetables | concat: furniture -%}
    {%- for item in everything %}
    - {{ item }}
    {%- endfor %}
    """
    assert (
        Liquid(tpl).render()
        == """
    - apples
    - oranges
    - peaches
    - carrots
    - turnips
    - potatoes
    - chairs
    - tables
    - shelves
    """
    )


# for coverage
def test_dot(set_default_standard):
    a = lambda: None
    setattr(a, "a-b", 1)
    b = lambda: None
    setattr(b, "a-b", 2)
    assert (
        Liquid("{{a | where: 'a-b', 1 | map: 'a-b' | first}}").render(a=[a, b])
        == "1"
    )


@pytest.mark.parametrize(
    "tpl,out",
    [
        ('{{ 0 | date: "%s"  | plus: 86400 }}', "86400"),
        ('{{ "now" | date: "%Y"  | plus: 1 }}', str(datetime.today().year + 1)),
        ('{{ 0 | date: "%s"  | minus: 86400 }}', "-86400"),
        ('{{ 0 | date: "%s"  | times: 86400 }}', "0"),
        ('{{ 1 | date: "%s"  | times: 86400 }}', "86400"),
        ('{{ 10 | date: "%s"  | divided_by: 2 | int }}', "5"),
        ('{{ 10 | date: "%s"  | modulo: 3 }}', "1"),
    ],
)
def test_date_arithmetic(tpl, out, set_default_standard):
    assert Liquid(tpl).render() == out


def test_emptydrop(set_default_standard):
    assert Liquid("{{ obj | sort_natural}}").render(obj=[]) == ""
    assert (
        Liquid("{{ obj | sort | bool}}", mode="wild").render(obj=[]) == "False"
    )
    assert (
        Liquid("{{ slice(obj, 0) == False}}", mode="wild").render(obj=[])
        == "True"
    )
    assert (
        Liquid("{{ uniq(obj) != False}}", mode="wild").render(obj=[])
        == "False"
    )


def test_regex_replace(set_default_standard):
    assert Liquid('{{1 | regex_replace: "a"}}').render() == "1"
    assert Liquid('{{"abc" | regex_replace: "a", "b"}}').render() == "bbc"
    assert (
        Liquid(
            '{{"abc" | regex_replace: "A", "b", case_sensitive=False}}'
        ).render()
        == "bbc"
    )

def test_basic_typecasting(set_default_standard):
    assert Liquid('{{ "1" | int | plus: 1 }}').render() == "2"
    assert Liquid('{{ "1" | float | plus: 1 }}').render() == "2.0"
    assert Liquid('{{ 1 | str | append: "1" }}').render() == "11"
    assert Liquid('{{ 1 | bool }}').render() == "True"
    assert Liquid('{{ int("1") | plus: 1 }}').render() == "2"
    assert Liquid('{{ float("1") | plus: 1 }}').render() == "2.0"
    assert Liquid('{{ str(1) | append: "1" }}').render() == "11"
    assert Liquid('{{ bool(1) }}').render() == "True"
