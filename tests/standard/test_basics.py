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
    ''',
        liquid_config={'debug': True}).render(
        user={'name': 'Adam'}
    ) == 'Hello Adam!'
