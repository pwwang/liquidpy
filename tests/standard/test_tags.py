"""Tests grabbed from:
https://shopify.github.io/liquid/tags/comment/
"""
from jinja2.exceptions import TemplateSyntaxError
import pytest

from liquid import Liquid


def test_comment(set_default_standard):
    tpl = """Anything you put between {% comment %} and {% endcomment %} tags
is turned into a comment."""
    Liquid(
        tpl
    ).render() == """Anything you put between  tags
is turned into a comment."""


def test_if(set_default_standard):
    tpl = """
    {% if product.title == "Awesome Shoes" %}
      These shoes are awesome!
    {% endif %}
    """
    assert (
        Liquid(tpl).render(product={"title": "Awesome Shoes"}).strip()
        == "These shoes are awesome!"
    )


def test_unless(set_default_standard):
    tpl = """
    {% unless product.title == "Awesome Shoes" %}
      These shoes are not awesome.
    {% endunless %}
    """
    assert (
        Liquid(tpl).render(product={"title": "Not Awesome Shoes"}).strip()
        == "These shoes are not awesome."
    )

    # in python:
    # bool(0.0) == False
    # bool("") == False
    # assert Liquid('{% unless "" %}1{% endunless %}').render() == ""
    assert Liquid('{% unless "" %}{% else %}1{% endunless %}').render() == ""
    assert Liquid("{% unless 0.0 %}{% else %}1{% endunless %}").render() == ""
    assert Liquid("{% unless empty %}1{% endunless %}").render() == "1"


def test_else_elsif(set_default_standard):
    tpl = """
    {% if customer.name == "kevin" %}
    Hey Kevin!
    {% elsif customer.name == "anonymous" %}
    Hey Anonymous!
    {% else %}
    Hi Stranger!
    {% endif %}
    """
    assert (
        Liquid(tpl).render(customer={"name": "anonymous"}).strip()
        == "Hey Anonymous!"
    )


def test_case_when(set_default_standard):
    tpl = """
    {% assign handle = handle %}
    {% case handle %}
        {% when "cake" %}
            This is a cake
        {% when "cookie" %}
            This is a cookie
        {% else %}
            This is not a cake nor a cookie
    {% endcase %}
    """
    assert Liquid(tpl).render(handle="cake").strip() == "This is a cake"

    assert (
        Liquid(
            """
    {% case true %}
    {% when false %}
    {% endcase %}
    """
        )
        .render()
        .strip()
        == ""
    )


def test_for(set_default_standard):
    tpl = """
    {%- for product in collection.products %} {{ product.title }}
    {%- endfor -%}
    """
    assert (
        Liquid(tpl).render(
            collection={
                "products": [
                    {"title": "hat"},
                    {"title": "shirt"},
                    {"title": "pants"},
                ]
            }
        )
        == " hat shirt pants"
    )

    tpl = """
    {%- for product in collection.products %}
      {{ product.title }}
    {% else %}
      The collection is empty.
    {%- endfor -%}
    """
    assert (
        Liquid(tpl).render(collection={"products": []}).strip()
        == "The collection is empty."
    )

    assert (
        Liquid("{{(1..5) | list}}", filters={"list": list}).render()
        == "[1, 2, 3, 4, 5]"
    )

    tpl = """
    {% for i in (1..5) %}
    {% if i == 4 %}
        {% break %}
    {% else %}
        {{ i }}
    {% endif %}
    {% endfor %}
    """
    assert Liquid(tpl).render().split() == ["1", "2", "3"]


def test_for_continue(set_default_standard):
    tpl = """
    {% for i in (1..5) %}
    {% if i == 4 %}
        {% continue %}
    {% else %}
        {{ i }}
    {% endif %}
    {% endfor %}
    """
    assert Liquid(tpl).render().split() == ["1", "2", "3", "5"]


def test_forloop(set_default_standard):
    tpl = """
    {% for product in products %}
        {% if forloop.first == true %}
            First time through!
        {% else %}
            Not the first time.
        {% endif %}
    {% endfor %}
    """
    rendered = Liquid(tpl).render(products=range(5)).splitlines()
    rendered = [ren.strip() for ren in rendered if ren.strip()]
    assert rendered == [
        "First time through!",
        "Not the first time.",
        "Not the first time.",
        "Not the first time.",
        "Not the first time.",
    ]

    tpl = """
    {% for product in products %}
        {{ forloop.index }}
    {% else %}
        // no products in your frontpage collection
    {% endfor %}
    """
    assert Liquid(tpl).render(products=range(5)).split() == [
        "1",
        "2",
        "3",
        "4",
        "5",
    ]

    # forloop outside for-loop
    assert Liquid("{{forloop}}").render(forloop=1) == "1"


def test_forloop_index0(set_default_standard):
    tpl = """
    {% for product in products %}
        {{ forloop.index0 }}
    {% endfor %}
    """
    assert Liquid(tpl).render(products=range(5)).split() == [
        "0",
        "1",
        "2",
        "3",
        "4",
    ]

    tpl = """
    {% for product in products %}
        {% if forloop.last == true %}
            This is the last iteration!
        {% else %}
            Keep going...
        {% endif %}
    {% endfor %}
    """
    rendered = Liquid(tpl).render(products=range(5)).splitlines()
    rendered = [ren.strip() for ren in rendered if ren.strip()]
    assert rendered == [
        "Keep going...",
        "Keep going...",
        "Keep going...",
        "Keep going...",
        "This is the last iteration!",
    ]

    tpl = """
    {% for product in products %}
        {% if forloop.first %}
        <p>This collection has {{ forloop.length }} products:</p>
        {% endif %}
        <p>{{ product.title }}</p>
    {% endfor %}
    """
    rendered = (
        Liquid(tpl)
        .render(
            products=[
                {"title": "Apple"},
                {"title": "Orange"},
                {"title": "Peach"},
                {"title": "Plum"},
            ]
        )
        .splitlines()
    )
    rendered = [ren.strip() for ren in rendered if ren.strip()]
    assert rendered == [
        "<p>This collection has 4 products:</p>",
        "<p>Apple</p>",
        "<p>Orange</p>",
        "<p>Peach</p>",
        "<p>Plum</p>",
    ]

    tpl = """
    {% for product in products %}
        {{ forloop.rindex }}
    {% endfor %}
    """
    assert Liquid(tpl).render(products=range(5)).split() == [
        "5",
        "4",
        "3",
        "2",
        "1",
    ]

    tpl = """
    {% for product in products %}
        {{ forloop.rindex0 }}
    {% endfor %}
    """
    assert Liquid(tpl).render(products=range(5)).split() == [
        "4",
        "3",
        "2",
        "1",
        "0",
    ]


def test_for_params(set_default_standard):
    tpl = """
    {% for item in array limit:2 %}
      {{ item }}
    {% endfor %}
    """
    assert Liquid(tpl).render(array=[1, 2, 3, 4, 5, 6]).split() == ["1", "2"]

    tpl = """
    {% for item in array offset:2 %}
      {{ item }}
    {% endfor %}
    """
    assert Liquid(tpl).render(array=[1, 2, 3, 4, 5, 6]).split() == [
        "3",
        "4",
        "5",
        "6",
    ]

    tpl = """
    {% for item in array limit:2 offset:2 %}
      {{ item }}
    {% endfor %}
    """
    assert Liquid(tpl).render(array=[1, 2, 3, 4, 5, 6]).split() == ["3", "4"]

    tpl = """
    {% for i in (3..5) %}
      {{ i }}
    {% endfor %}
    {% assign num = 4 %}
    {% for i in (1..num) %}
      {{ i }}
    {% endfor %}
    """
    assert Liquid(tpl).render().split() == ["3", "4", "5", "1", "2", "3", "4"]


def test_for_reversed(set_default_standard):
    tpl = """
    {% for item in array reversed %}
      {{ item }}
    {% endfor %}
    """
    assert Liquid(tpl).render(array=[1, 2, 3, 4, 5, 6]).split() == [
        "6",
        "5",
        "4",
        "3",
        "2",
        "1",
    ]


def test_for_cycle(set_default_standard):
    tpl = """
    {% for i in (1..4) %}
        {% cycle "one", "two", "three" %}
    {% endfor %}
    """
    assert Liquid(tpl).render().split() == [
        "one",
        "two",
        "three",
        "one",
    ]

    tpl = """
    {% for i in (1..2) %}
        {% cycle "first": "one", "two", "three" %}
        {% cycle "second": "one", "two", "three" %}
    {% endfor %}
    """
    assert Liquid(tpl).render().split() == [
        "one",
        "one",
        "two",
        "two",
    ]


def test_tablerow(set_default_standard):
    tpl = """
    <table>
    {% tablerow product in collection.products %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        }
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Cool Shirt
    </td><td class="col2">
      Alien Poster
    </td><td class="col3">
      Batman Poster
    </td><td class="col4">
      Bullseye Shirt
    </td><td class="col5">
      Another Classic Vinyl
    </td><td class="col6">
      Awesome Jeans
    </td></tr>
    </table>
    """
    )

    tpl = """
    <table>
    {% tablerow product in collection.products cols:2 %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        }
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Cool Shirt
    </td><td class="col2">
      Alien Poster
    </td></tr><tr class="row2"><td class="col1">
      Batman Poster
    </td><td class="col2">
      Bullseye Shirt
    </td></tr><tr class="row3"><td class="col1">
      Another Classic Vinyl
    </td><td class="col2">
      Awesome Jeans
    </td></tr>
    </table>
    """
    )

    tpl = """
    <table>
    {% tablerow product in collection.products cols:2 limit:3 %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        }
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Cool Shirt
    </td><td class="col2">
      Alien Poster
    </td></tr><tr class="row2"><td class="col1">
      Batman Poster
    </td></tr>
    </table>
    """
    )

    tpl = """
    <table>
    {% tablerow product in collection.products cols:2 limit:lim %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        },
        lim=3
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Cool Shirt
    </td><td class="col2">
      Alien Poster
    </td></tr><tr class="row2"><td class="col1">
      Batman Poster
    </td></tr>
    </table>
    """
    )


    tpl = """
    <table>
    {% tablerow product in collection.products cols:2 offset:3 %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        }
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Bullseye Shirt
    </td><td class="col2">
      Another Classic Vinyl
    </td></tr><tr class="row2"><td class="col1">
      Awesome Jeans
    </td></tr>
    </table>
    """
    )

    tpl = """
    <table>
    {% tablerow product in collection.products cols:2 limit:2 offset:3 %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """

    rendered = Liquid(tpl).render(
        collection={
            "products": [
                {"title": "Cool Shirt"},
                {"title": "Alien Poster"},
                {"title": "Batman Poster"},
                {"title": "Bullseye Shirt"},
                {"title": "Another Classic Vinyl"},
                {"title": "Awesome Jeans"},
            ]
        }
    )

    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
      Bullseye Shirt
    </td><td class="col2">
      Another Classic Vinyl
    </td></tr>
    </table>
    """
    )

    tpl = """{% assign num = 4 %}
    <table>
    {% tablerow i in (1..num) %}
    {{ i }}
    {% endtablerow %}
    </table>

    <table>
    {% tablerow i in (3..5) %}
    {{ i }}
    {% endtablerow %}
    </table>
    """
    rendered = Liquid(tpl).render()
    assert (
        rendered
        == """
    <table>
    <tr class="row1"><td class="col1">
    1
    </td><td class="col2">
    2
    </td><td class="col3">
    3
    </td><td class="col4">
    4
    </td></tr>
    </table>

    <table>
    <tr class="row1"><td class="col1">
    3
    </td><td class="col2">
    4
    </td><td class="col3">
    5
    </td></tr>
    </table>
    """
    )


def test_raw(set_default_standard):
    tpl = """
    {%- raw %}
      In Handlebars, {{ this }} will be HTML-escaped, but
      {{{ that }}} will not.
    {% endraw -%}
    """
    assert (
        Liquid(tpl).render()
        == """
      In Handlebars, {{ this }} will be HTML-escaped, but
      {{{ that }}} will not.
    """
    )


def test_assign(set_default_standard):
    assert Liquid("{% assign x = 'bar' %}{{x}}").render() == "bar"


def test_capture(set_default_standard):
    tpl = """{% capture my_variable %}I am being captured.{% endcapture -%}
    {{ my_variable }}"""
    assert Liquid(tpl).render() == "I am being captured."

    tpl = """
    {% assign favorite_food = "pizza" %}
    {% assign age = 35 %}

    {% capture about_me %}
    I am {{ age }} and my favorite food is {{ favorite_food }}.
    {% endcapture %}

    {{ about_me }}
    """
    assert Liquid(tpl).render().strip() == (
        "I am 35 and my favorite food is pizza."
    )


def test_xcrement(set_default_standard):
    tpl = """
    {% increment my_counter %}
    {% increment my_counter %}
    {% increment my_counter %}
    """
    assert Liquid(tpl).render().split() == ["0", "1", "2"]

    tpl = """
    {% decrement my_counter %}
    {% decrement my_counter %}
    {% decrement my_counter %}
    """
    assert Liquid(tpl).render().split() == ["-1", "-2", "-3"]


def test_comment_with_prefix(set_default_standard):
    tpl = """{% comment "#" %}
    a
    b
    {%endcomment%}
    """
    Liquid(tpl).render() == """# a\n# b\n"""


def test_unless_elif(set_default_standard):
    tpl = """
    {% unless a == 1 %}
    11
    {% elif a == 2 %}
    22
    {% else %}
    33
    {% endunless %}
    """
    assert Liquid(tpl).render(a=1).strip() == "22"
    assert Liquid(tpl).render(a=2).strip() == "11"


def test_case_when_error(set_default_standard):
    with pytest.raises(TemplateSyntaxError, match="Expected nothing"):
        Liquid("{% case a %}0{% when 1 %}1{% endcase %}")

    with pytest.raises(
        TemplateSyntaxError, match="Expected 'begin of statement block'"
    ):
        Liquid("{% case a %}")


def test_tablerow_arg_error(set_default_standard):
    tpl = """
    <table>
    {% tablerow product in collection.products limit:"a" %}
      {{ product.title }}
    {% endtablerow %}
    </table>
    """
    with pytest.raises(
        TemplateSyntaxError, match="Expected an integer or a variable"
    ):
        Liquid(tpl)

def test_unknown_tag(set_default_standard):
    with pytest.raises(TemplateSyntaxError, match="unknown tag"):
        Liquid("{% a %} {% enda %}")
