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
    )
    assert template.render(values=[None, False]) == "good|nil|false|blank"


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
    )
    assert template.render(
        item={"title": "foo", "some": "thing"},
        text="cba",
        values=[{"title": None}, {"title": "x"}],
        rejected=[
            {"title": "keep", "active": True},
            {"title": "drop", "active": False},
        ],
    ) == "foo|abc|None|keep"


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
