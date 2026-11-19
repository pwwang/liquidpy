import pytest  # noqa: F401
from liquid import Liquid


def test_filter(set_default_shopify):
    assert Liquid('').render() == ''


def test_shopify_special_values_and_comparisons(set_default_shopify):
    template = Liquid(
        "{% if 1 == true %}bad{% else %}good{% endif %}"
        "|{% if values contains nil %}nil{% endif %}"
        "|{% if values contains false %}false{% endif %}"
        "|{% if nil == blank %}blank{% endif %}"
        "|{% if blank %}truthy{% endif %}"
    )
    assert template.render(values=[1, 2, None, False]) == "good|||blank|truthy"


def test_shopify_blank_empty_and_nil(set_default_shopify):
    template = Liquid(
        "{% if '' == blank and '' == empty and blank != empty %}"
        "special{% endif %}|{{ nil }}|{{ nosuchthing }}"
    )
    assert template.render() == "special||"


def test_shopify_missing_values_and_numeric_filters(set_default_shopify):
    template = Liquid(
        "{{ 5 | at_least: nosuchthing }}"
        "|{{ 9.0 | divided_by: 2 }}"
        "|{{ 2.5 | round }}"
        "|{{ -2.5 | round }}"
        "|{{ 2.55 | round: 1 }}"
    )
    assert template.render() == "5|4.5|3|-3|2.6"


def test_shopify_collection_filters(set_default_shopify):
    template = Liquid(
        "{{ item | map: 'title' | join: '#' }}"
        "|{{ text | sort | join: '' }}"
        "|{{ values | where: 'title', nil | map: 'title' | join: ',' }}"
        "|{{ rejected | reject: 'active', false | map: 'title' | join: ',' }}"
        "|{{ 'BzAa4' | sort | join: '#' }}"
        "|{{ a | reject: 'c' }}"
        "|{{ (1..5) | slice: 1, 3 }}"
    )
    assert template.render(
        item={"title": "foo", "some": "thing"},
        text="cba",
        values=[{"title": None}, {"title": "x"}],
        rejected=[
            {"title": "keep", "active": True},
            {"title": "drop", "active": False},
        ],
        a=["x", "y", "cat", None],
    ) == "foo|cba|x|keep|BzAa4||..5"


def test_shopify_where_nil_and_hash_iteration(set_default_shopify):
    template = Liquid(
        "{% assign filtered = items | where: 'b', nil %}"
        "{% for item in filtered %}{% for pair in item %}"
        "({{ pair[0] }},{{ pair[1] }}){% endfor %}{% endfor %}"
    )
    assert template.render(
        items=[{"b": False}, {"b": "bar"}, {"b": None}]
    ) == "(b,bar)"


def test_shopify_truncatewords_zero(set_default_shopify):
    template = Liquid('{{ "one two three four" | truncatewords: 0 }}')
    assert template.render() == "one..."


def test_shopify_round_and_whitespace_filters(set_default_shopify):
    template = Liquid(
        "{{ nosuchthing | round: 2 }}|{{ 5.666 | round: -2 }}"
        "|{{ 5 | lstrip }}|{{ padded | rstrip }}"
    )
    assert template.render(padded="hello \t\r\n ") == "0|0|5|hello"


def test_shopify_string_filters(set_default_shopify):
    template = Liquid(
        "{{ text | newline_to_br }}"
        "|{{ html | strip_html }}"
        "|{{ encoded | url_decode }}"
    )
    assert template.render(
        text="one\ntwo",
        html="<script>hidden</script>shown",
        encoded="a+b",
    ) == "one<br />\ntwo|shown|a b"
