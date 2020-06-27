"""Tests grabbed from:
https://shopify.github.io/liquid/basics
"""
import pytest

from liquid import Liquid

def test_introduction():
    assert Liquid('{{page.title}}').render(
        page={'title': 'Introduction'}
    ) == 'Introduction'

def test_tags():
    assert Liquid('''
        {%- if user -%}
        Hello {{ user.name }}!
        {%- endif -%}
    ''').render(
        user={'name': 'Adam'}
    ) == 'Hello Adam!'

def test_filters():
    assert Liquid('{{ "/my/fancy/url" | append: ".html" }}').render() == (
        '/my/fancy/url.html'
    )

    assert Liquid('{{ "adam!" | capitalize | prepend: "Hello " }}').render() ==(
        "Hello Adam!"
    )

def test_operators():
    tpl = """
    {%- if product.title == "Awesome Shoes" -%}
      These shoes are awesome!
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={'title': 'Awesome Shoes'}) == (
        'These shoes are awesome!'
    )

    tpl = """
    {%- if product.type == "Shirt" or product.type == "Shoes" -%}
      This is a shirt or a pair of shoes.
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={'type': 'Shirt'}) == (
        'This is a shirt or a pair of shoes.'
    )

    tpl = """
    {%- if product.title contains "Pack" -%}
      This product's title contains the word Pack.
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={'title': 'Show Pack'}) == (
        "This product's title contains the word Pack."
    )

    tpl = """
    {%- if product.tags contains "Hello" -%}
      This product has been tagged with "Hello".
    {%- endif -%}
    """
    assert Liquid(tpl).render(product={'tags': 'Hello Pack'}) == (
        'This product has been tagged with "Hello".'
    )

    tpl = """
    {%- if true or false and false -%}
      This evaluates to true, since the `and` condition is checked first.
    {%- endif -%}
    """
    assert Liquid(tpl).render() == (
        "This evaluates to true, since the `and` condition is checked first."
    )

    tpl = """
    {%- if true and false and false or true %}
    This evaluates to false, since the tags are checked like this:

    true and (false and (false or true))
    true and (false and true)
    true and false
    false
    {% endif -%}
    """
    assert Liquid(tpl).render() == ''



