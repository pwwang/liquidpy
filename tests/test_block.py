"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/block_unit_test.rb
"""
import pytest
from liquid.parser import Parser
from liquid.config import Config
from liquid.utils import template_meta

def parse(template):
    config = Config(debug='more')
    config.update_logger()
    meta = template_meta(template)
    parser = Parser(meta, config)
    return parser.parse()

def test_blankspace():
    parsed = parse("  ")
    assert parsed.name == "ROOT"
    assert len(parsed.children) == 1

def test_variable_beginning():
    parsed = parse("{{funk}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'OUTPUT'
    assert parsed.children[1].name == 'LITERAL'

    parsed = parse("{{-funk}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'OUTPUT'
    assert parsed.children[1].name == 'LITERAL'

    parsed = parse("{{funk-}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'OUTPUT'
    assert parsed.children[1].name == 'LITERAL'

    parsed = parse("{{-funk-}}  ")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'OUTPUT'
    assert parsed.children[1].name == 'LITERAL'

def test_variable_end():
    parsed = parse("  {{funk}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    parsed = parse("  {{-funk}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    parsed = parse("  {{funk-}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    parsed = parse("  {{-funk-}}")
    assert len(parsed.children) == 2
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'

def test_variable_middle():
    parsed = parse("  {{funk}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    assert parsed.children[2].name == 'LITERAL'
    parsed = parse("  {{-funk}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    assert parsed.children[2].name == 'LITERAL'
    parsed = parse("  {{funk-}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    assert parsed.children[2].name == 'LITERAL'
    parsed = parse("  {{-funk-}}  ")
    assert len(parsed.children) == 3
    assert parsed.children[0].name == 'LITERAL'
    assert parsed.children[1].name == 'OUTPUT'
    assert parsed.children[2].name == 'LITERAL'

def test_variable_many_embedded_fragments():
    parsed = parse("  {{funk}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{-funk}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk-}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{-so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{so}} {{-brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{so}} {{brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{-funk-}} {{so}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{-so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{so}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{-funk-}} {{-so-}} {{brother}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{funk}} {{-so-}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{-funk-}} {{so}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]
    parsed = parse("  {{-funk-}} {{-so-}} {{-brother-}} ")
    assert len(parsed.children) == 7
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'OUTPUT', 'LITERAL', 'OUTPUT',
        'LITERAL', 'OUTPUT', 'LITERAL'
    ]

def test_with_block():
    parsed = parse("  {% assign x = 1 %}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign'
    ]
    parsed = parse("  {%- assign x = 1 %}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign'
    ]
    parsed = parse("  {% assign x = 1 -%}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign'
    ]
    parsed = parse("  {%- assign x = 1 -%}")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign'
    ]
    parsed = parse("{% assign x = 1 %}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', 'LITERAL'
    ]
    parsed = parse("{%- assign x = 1 %}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', 'LITERAL'
    ]
    parsed = parse("{% assign x = 1 -%}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', 'LITERAL'
    ]
    parsed = parse("{%- assign x = 1 -%}  ")
    assert len(parsed.children) == 2
    assert [child.name for child in parsed.children] == [
        'assign', 'LITERAL'
    ]
    parsed = parse("  {% assign x = 1 %}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign', 'LITERAL'
    ]
    parsed = parse("  {%- assign x = 1 %}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign', 'LITERAL'
    ]
    parsed = parse("  {% assign x = 1 -%}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign', 'LITERAL'
    ]
    parsed = parse("  {%- assign x = 1 -%}  ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'assign', 'LITERAL'
    ]

    parsed = parse("  {% comment %} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {%- comment %} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {% comment -%} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {% comment %} {%- endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {% comment %} {% endcomment -%} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {%- comment -%} {% endcomment %} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]
    parsed = parse("  {% comment %} {%- endcomment -%} ")
    assert len(parsed.children) == 3
    assert [child.name for child in parsed.children] == [
        'LITERAL', 'comment', 'LITERAL'
    ]

def test_escape():
    parsed = parse("\\{% comment %} \\{% endcomment %}")
    assert len(parsed.children) == 1
    assert parsed.children[0].name == 'LITERAL'

def test_custom_tag():
    from liquid import tag_manager
    from liquid.tags import Tag
    @tag_manager.register
    class TagTesttag(Tag):
        VOID = False

    parsed = parse("{% testtag %} {% endtesttag %}")
    assert len(parsed.children) == 1
    assert parsed.children[0].name == 'testtag'
