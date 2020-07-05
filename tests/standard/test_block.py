"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/block_unit_test.rb
"""
import pytest
import logging
from functools import partial
from liquid.parser import StandardParser as Parser
from liquid.config import Config, LIQUID_LOGGER_NAME

@pytest.fixture
def parse():
    config = Config()
    config.logger = logging.getLogger(LIQUID_LOGGER_NAME)
    return partial(Parser(config).parse, template_name='<string>')

def test_blankspace(parse):
    parsed = parse("  ")
    assert parsed.name == 'ROOT'
    assert len(parsed.children) == 1

def test_variable_beginning(parse):
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

def test_variable_end(parse):
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

def test_variable_middle(parse):
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

def test_variable_many_embedded_fragments(parse):
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

def test_with_block(parse):
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

def test_custom_tag(parse):
    from liquid import register_tag
    from liquid.tag import Tag
    @register_tag
    class TagTesttag(Tag):
        VOID = False
        SYNTAX = """
        inner_tag: tag_testtag
        !tag_testtag: $tagnames number
        """

        def t_tag_testtag(self, tagname, data):
            return TagTesttag(tagname, data)

    parsed = parse("{% testtag 1 %} {% endtesttag %}")
    assert len(parsed.children) == 1
    assert parsed.children[0].name == 'testtag'
