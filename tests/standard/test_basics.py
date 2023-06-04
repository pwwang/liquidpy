"""Tests grabbed from:
https://shopify.github.io/liquid/basics
"""
import pytest

from liquid import Liquid, unpatch_jinja


def test_introduction(set_default_standard):
    assert (
        Liquid("{{page.title}}").render(page={"title": "Introduction"})
        == "Introduction"
    )


def test_tags(set_default_standard):
    assert (
        Liquid(
            """
        {%- if user -%}
        Hello {{ user.name }}!
        {%- endif -%}
    """
        ).render(user={"name": "Adam"})
        == "Hello Adam!"
    )


def test_filters(set_default_standard):
    assert Liquid('{{ "/my/fancy/url" | append: ".html" }}').render() == (
        "/my/fancy/url.html"
    )

    assert Liquid(
        '{{ "adam!" | capitalize | prepend: "Hello " }}'
    ).render() == ("Hello Adam!")
    # test keyword argument
    assert Liquid(
        '{{ "hello adam!" | replace_first: "adam", new:"Adam" | remove: "hello "}}'
    ).render() == ("Adam!")


def test_operators(set_default_standard):
    tpl = """
    {%- if product.title == "Awesome Shoes" -%}
      These shoes are awesome!
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={"title": "Awesome Shoes"}) == (
        "These shoes are awesome!"
    )

    tpl = """
    {%- if product.type == "Shirt" or product.type == "Shoes" -%}
      This is a shirt or a pair of shoes.
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={"type": "Shirt"}) == (
        "This is a shirt or a pair of shoes."
    )

    tpl = """
    {%- if product.title contains "Pack" -%}
      This product's title contains the word Pack.
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={"title": "Show Pack"}) == (
        "This product's title contains the word Pack."
    )

    tpl = """
    {%- if product.tags contains "Hello" -%}
      This product has been tagged with "Hello".
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={"tags": "Hello Pack"}) == (
        'This product has been tagged with "Hello".'
    )


def test_or_and(set_default_standard):
    tpl = """
    {%- if true or false and false -%}
      This evaluates to true, since the `and` condition is checked first.
    {%- endif -%}
    """
    assert Liquid(tpl).render() == (
        "This evaluates to true, since the `and` condition is checked first."
    )

# This is a different behavior than in standard liquid
def test_multiple_and_or(set_default_standard):
    # tpl = """
    # {%- if true and false and false or true %}
    # This evaluates to false, since the tags are checked like this:

    # true and (false and (false or true))
    # true and (false and true)
    # true and false
    # false
    # {% endif -%}
    # """
    # assert Liquid(tpl).render() == ""

    tpl = """
    {%- if true and false and true or false %}
    This evaluates to false, since the tags are checked like this:

    (true and false) and true or false
    (false and true) or false
    (false or false)
    false
    {% endif -%}
    """
    assert Liquid(tpl).render() == ""


def test_truthy_falsy(set_default_standard):
    tpl = """
    {% assign tobi = "Tobi" %}

    {% if tobi %}
      This condition will always be true.
    {% endif %}
    """
    assert Liquid(tpl).render().strip() == "This condition will always be true."

    tpl = """
    {% if settings.fp_heading %}
      <h1>{{ settings.fp_heading }}</h1>
    {% endif %}
    """
    assert (
        # Liquid(tpl).render(settings={"fp_heading": ""}).strip() == "<h1></h1>"
        # "" tests false in python, instead of true in liquid
        Liquid(tpl).render(settings={"fp_heading": " "}).strip() == "<h1> </h1>"
    )


def test_types(set_default_standard):
    tpl = "The current user is {{ user.name }}"
    assert Liquid(tpl).render(user={}) == "The current user is "

    tpl = """
    {%- for user in site.users %} {{ user }}
    {%- endfor -%}
    """
    assert (
        Liquid(tpl).render(site={"users": ["Tobi", "Laura", "Tetsuro", "Adam"]})
        == " Tobi Laura Tetsuro Adam"
    )

    tpl = "{{ site.users[0] }} {{ site.users[1] }} {{ site.users[3] }}"
    assert (
        Liquid(tpl).render(site={"users": ["Tobi", "Laura", "Tetsuro", "Adam"]})
        == "Tobi Laura Adam"
    )


def test_wscontrol(set_default_standard):
    tpl = """
{% assign my_variable = "tomato" %}
{{ my_variable }}"""

    assert Liquid(tpl).render() == "\n\ntomato"
    tpl = """
{%- assign my_variable = "tomato" -%}
{{ my_variable }}"""

    assert Liquid(tpl).render() == "tomato"

    tpl = """{% assign username = "John G. Chalmers-Smith" %}
{% if username and username.size > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}"""
    assert (
        Liquid(tpl).render()
        == "\n\n  Wow, John G. Chalmers-Smith, you have a long name!\n"
    )

    tpl = """{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and username.size > 10 -%}
  Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif -%}"""
    assert (
        Liquid(tpl).render()
        == "Wow, John G. Chalmers-Smith, you have a long name!"
    )


def test_indention_keeping(set_default_standard):
    tpl = """
        1
        {{* var }}
        2
    """
    out = Liquid(tpl).render({"var": "a\n  b"})
    assert out == """
        1
        a
          b
        2
    """
