from types import SimpleNamespace

import pytest  # noqa: F401
from jinja2 import Undefined
from liquid import Liquid
from liquid.filters.shopify import (
    _ShopifyDrop,
    at_least,
    divided_by,
    liquid_contains,
    liquid_equal,
    liquid_map,
    reject,
    round as shopify_round,
    shopify_join,
    shopify_lstrip,
    shopify_rstrip,
    shopify_slice,
    shopify_truncatewords,
    sort,
    where,
)


def test_shopify_drop_and_comparison_helpers():
    missing = Undefined(name="missing")
    assert str(_ShopifyDrop("blank")) == ""
    assert _ShopifyDrop("blank") + "value" == "value"
    assert "value" + _ShopifyDrop("blank") == "value"
    assert _ShopifyDrop("blank").split() == []
    assert list(_ShopifyDrop("blank")) == []
    assert _ShopifyDrop("empty") == []
    assert liquid_equal(missing, None)
    assert liquid_equal(None, missing)
    assert liquid_equal({"key": [1]}, {"key": [1]})
    assert liquid_equal([True], [True])
    assert not liquid_equal([1], (1,))
    assert not liquid_equal(1, True)
    assert liquid_contains("abc", "b")
    assert not liquid_contains("abc", 1)
    assert liquid_contains([{"key": 1}], {"key": 1})
    assert not liquid_contains([1], None)
    assert not liquid_contains([False], False)
    assert not liquid_contains(1, "value")


def test_shopify_filter_fallbacks_and_collections():
    missing = Undefined(name="missing")
    assert at_least(5, missing) == 5
    assert at_least(None, 5) == 5
    assert at_least(3, 5) == 5
    assert divided_by(5, 2) == 2
    assert divided_by(5, True) == 5
    assert shopify_round(None) == 0
    assert shopify_round(2.5, "invalid") == 3
    assert liquid_map(missing, "key") == []
    assert liquid_map({"key": 1}, "absent") == []
    assert liquid_map({"key": 1}, "key") == [1]
    assert liquid_map([{"key": 1}], missing) == []
    assert liquid_map(["text"], "upper") == [None]
    assert liquid_map([SimpleNamespace(key=1)], "key") == [1]
    assert liquid_map([SimpleNamespace(key=lambda: 1)], "key") == [None]
    assert sort(missing) == []
    assert sort([3, 1], missing) == [1, 3]
    assert sort([{"key": 2}, {"key": 1}], "key") == [
        {"key": 1},
        {"key": 2},
    ]
    assert sort([1, "two"]) is None
    assert where(None, "key") == []
    assert where([{"key": True}, {"key": False}], "key") == [{"key": True}]
    assert where([{"key": True}], "key", True) == [{"key": True}]
    assert where([{"key": True}], "key", missing) == [{"key": True}]
    assert reject(missing, "key") == []
    assert reject("abc", "b", False) == ["abc"]
    assert reject([{"key": False}], "key", missing) == [{"key": False}]


def test_shopify_join_slice_and_whitespace_fallbacks():
    missing = Undefined(name="missing")
    assert shopify_join(None) == ""
    assert shopify_join(missing) == ""
    assert shopify_join([{"key": "value"}, None, missing], ":", "key") == (
        "value::"
    )
    assert shopify_truncatewords("one two", 2) == "one two"
    assert shopify_slice("", 0) == ""
    assert shopify_slice("abc", -1, None) == "c"
    assert shopify_lstrip(None) == ""
    assert shopify_lstrip(missing) == ""
    assert shopify_rstrip(None) == ""
    assert shopify_rstrip(missing) == ""


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
