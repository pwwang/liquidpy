"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/block_unit_test.rb
"""
import pytest
import logging
from functools import partial
from liquid.standard.parser import StandardParser as Parser
from liquid.config import Config, LIQUID_LOGGER_NAME

@pytest.fixture
def parse():
    config = Config()
    config.logger = logging.getLogger(LIQUID_LOGGER_NAME)
    return partial(Parser(config).parse, template_name='<string>')

def test_blankspace(parse):
    parsed = parse("  ")
    assert parsed.name == '__ROOT__'
    assert len(parsed.children) == 1

def test_variable_beginning(parse):
    parsed = parse("{{funk}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__OUTPUT__'
    assert parsed.children[1].name == '__LITERAL__'

    parsed = parse("{{-funk}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__OUTPUT__'
    assert parsed.children[1].name == '__LITERAL__'

    parsed = parse("{{funk-}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__OUTPUT__'
    assert parsed.children[1].name == '__LITERAL__'

    parsed = parse("{{-funk-}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__OUTPUT__'
    assert parsed.children[1].name == '__LITERAL__'

def test_variable_end(parse):
    parsed = parse("  {{funk}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    parsed = parse("  {{-funk}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    parsed = parse("  {{funk-}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    parsed = parse("  {{-funk-}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'

def test_variable_middle(parse):
    parsed = parse("  {{funk}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    assert parsed.children[2].name == '__LITERAL__'
    parsed = parse("  {{-funk}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    assert parsed.children[2].name == '__LITERAL__'
    parsed = parse("  {{funk-}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    assert parsed.children[2].name == '__LITERAL__'
    parsed = parse("  {{-funk-}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == '__LITERAL__'
    assert parsed.children[1].name == '__OUTPUT__'
    assert parsed.children[2].name == '__LITERAL__'

def test_variable_many_embedded_fragments(parse):
    parsed = parse("  {{funk}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{-funk}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk-}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{-so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{so}} {{-brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{so}} {{brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{-funk-}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{-so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{so}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{-funk-}} {{-so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{funk}} {{-so-}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{-funk-}} {{so}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]
    parsed = parse("  {{-funk-}} {{-so-}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', '__OUTPUT__', '__LITERAL__', '__OUTPUT__',
        '__LITERAL__', '__OUTPUT__', '__LITERAL__'
    ]

def test_with_block(parse):
    parsed = parse("  {% assign x = 1 %}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign'
    ]
    parsed = parse("  {%- assign x = 1 %}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign'
    ]
    parsed = parse("  {% assign x = 1 -%}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign'
    ]
    parsed = parse("  {%- assign x = 1 -%}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign'
    ]
    parsed = parse("{% assign x = 1 %}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', '__LITERAL__'
    ]
    parsed = parse("{%- assign x = 1 %}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', '__LITERAL__'
    ]
    parsed = parse("{% assign x = 1 -%}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', '__LITERAL__'
    ]
    parsed = parse("{%- assign x = 1 -%}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', '__LITERAL__'
    ]
    parsed = parse("  {% assign x = 1 %}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign', '__LITERAL__'
    ]
    parsed = parse("  {%- assign x = 1 %}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign', '__LITERAL__'
    ]
    parsed = parse("  {% assign x = 1 -%}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign', '__LITERAL__'
    ]
    parsed = parse("  {%- assign x = 1 -%}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'assign', '__LITERAL__'
    ]

    parsed = parse("  {% comment %} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {%- comment %} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {% comment -%} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {% comment %} {%- endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {% comment %} {% endcomment -%} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {%- comment -%} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]
    parsed = parse("  {% comment %} {%- endcomment -%} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        '__LITERAL__', 'comment', '__LITERAL__'
    ]

def test_custom_tag(parse):
    from liquid import register_tag
    from liquid.common.tagparser import Tag
    @register_tag
    class TagTesttag(Tag):
        VOID = False
        SYNTAX = '<EMPTY>'

    parsed = parse("{% testtag %} {% endtesttag %}")
    assert len(parsed.children) == 1
    assert parsed.children[0].name == 'testtag'
