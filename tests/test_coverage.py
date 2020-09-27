"""Just add tests for the codes that are not covered by other tests"""
import pytest
from liquid import *

def test_endtagunexpected():
    with pytest.raises(LiquidSyntaxError):
        Liquid("{% endif %}")

def test_child_unclosed():
    with pytest.raises(LiquidSyntaxError):
        Liquid("{% for i in (1..2) %}{% if i == 1 %}{{i}}{%else%}{% endfor %}")

def test_child_unclosed_2():
    with pytest.raises(LiquidSyntaxError):
        # if not closed
        Liquid("{% capture x %}{% if i == 1 %}{{i}}{%else%}{% endfor %}")

def test_child_unclosed_3():
    with pytest.raises(LiquidSyntaxError):
        # if not closed
        Liquid("{% case true %}{% when true %}{% endx %}")

def test_child_unclosed_4():
    with pytest.raises(LiquidSyntaxError):
        # if not closed
        Liquid("{% capture x %}{% if i == 1 %}{{i}}{% endfor %}")

def test_debug(caplog):
    tpl = """
    {%- assign array = "1,2,3,4,5" | split: "," %}
    {%- capture x %}
        {%- for i in array reversed %}
            {%- if forloop.index0 < 3 %}
                {%- cycle 1, 2 %}{{i}},
                {%- continue %}
            {%- else %}
                {%- break %}
            {%- endif %}
        {%- endfor %}
    {%- endcapture %}
    {%- case true %}
        {%- when false %}
            {{- "nothing" }}
        {%- else %}
            {%- assign x = x | strip | split: "," | join: ","%}
    {%- endcase %}
    {% increment x %}
    {% decrement y %}
    {{x}}
    """
    rendered = Liquid(tpl, liquid_config={'debug': True}).render()
    assert rendered == """
    0
    -1
    15,24,13,
    """
    text = caplog.text

    def assert_in(substr, txt):
        assert substr in txt
        return txt[txt.find(substr)+len(substr)+30:]

    text = assert_in("- PARSING '<string>' ...", text)

    text = assert_in("  Found <TagLITERAL('\\n    ', line 1, column 1)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 2, column: 5)", text)
    text = assert_in("  Found <TagAssign('array = \"1,2,3,4,5\" | [...]', line 2, column 16)>", text)
    text = assert_in("  Closed node: NodeTag(assign)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 2, column 51)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 3, column: 5)", text)
    text = assert_in("  Found <TagCapture('x', line 3, column 17)>", text)
    text = assert_in("  Closed node: NodeTag(capture)", text)
    text = assert_in("  Found <TagLITERAL('\\n        ', line 3, column 21)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 4, column: 9)", text)
    text = assert_in("  Found <TagFor('i in array reversed', line 4, column 17)>", text)
    text = assert_in("  Closed node: NodeTag(for)", text)
    text = assert_in("  Found <TagLITERAL('\\n            ', line 4, column 39)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 5, column: 13)", text)
    text = assert_in("  Found <TagIf('forloop.index0 < 3', line 5, column 20)>", text)
    text = assert_in("  Closed node: NodeTag(if)", text)
    text = assert_in("  Found <TagLITERAL('\\n                ', line 5, column 41)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 6, column: 17)", text)
    text = assert_in("  Found <TagCycle('1, 2', line 6, column 27)>", text)
    text = assert_in("  Closed node: NodeTag(cycle)", text)
    text = assert_in("  Opened potential node: NodeOutput (line: 6, column: 34)", text)
    text = assert_in("  Found <TagOUTPUT('i', line 6, column 36)>", text)
    text = assert_in("  Closed node: OUTPUT", text)
    text = assert_in("  Found <TagLITERAL(',\\n                ', line 6, column 39)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 7, column: 17)", text)
    text = assert_in("  Found <TagContinue('', line 7, column 29)>", text)
    text = assert_in("  Closed node: NodeTag(continue)", text)
    text = assert_in("  Found <TagLITERAL('\\n            ', line 7, column 32)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 8, column: 13)", text)
    text = assert_in("  Found <TagElse('', line 8, column 21)>", text)
    text = assert_in("  Closed node: NodeTag(else)", text)
    text = assert_in("  Found <TagLITERAL('\\n                ', line 8, column 24)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 9, column: 17)", text)
    text = assert_in("  Found <TagBreak('', line 9, column 26)>", text)
    text = assert_in("  Closed node: NodeTag(break)", text)
    text = assert_in("  Found <TagLITERAL('\\n            ', line 9, column 29)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 10, column: 13)", text)
    text = assert_in("  Found <TagEND('if', line 10, column 22)>", text)
    text = assert_in("  Closed node: NodeTag(endif)", text)
    text = assert_in("  Found <TagLITERAL('\\n        ', line 10, column 25)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 11, column: 9)", text)
    text = assert_in("  Found <TagEND('for', line 11, column 19)>", text)
    text = assert_in("  Closed node: NodeTag(endfor)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 11, column 22)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 12, column: 5)", text)
    text = assert_in("  Found <TagEND('capture', line 12, column 19)>", text)
    text = assert_in("  Closed node: NodeTag(endcapture)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 12, column 22)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 13, column: 5)", text)
    text = assert_in("  Found <TagCase('true', line 13, column 14)>", text)
    text = assert_in("  Closed node: NodeTag(case)", text)
    text = assert_in("  Found <TagLITERAL('\\n        ', line 13, column 21)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 14, column: 9)", text)
    text = assert_in("  Found <TagWhen('false', line 14, column 18)>", text)
    text = assert_in("  Closed node: NodeTag(when)", text)
    text = assert_in("  Found <TagLITERAL('\\n            ', line 14, column 26)>", text)
    text = assert_in("  Opened potential node: NodeOutput (line: 15, column: 13)", text)
    text = assert_in("  Found <TagOUTPUT('\"nothing\"', line 15, column 17)>", text)
    text = assert_in("  Closed node: OUTPUT", text)
    text = assert_in("  Found <TagLITERAL('\\n        ', line 15, column 29)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 16, column: 9)", text)
    text = assert_in("  Found <TagElse('', line 16, column 17)>", text)
    text = assert_in("  Closed node: NodeTag(else)", text)
    text = assert_in("  Found <TagLITERAL('\\n            ', line 16, column 20)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 17, column: 13)", text)
    text = assert_in("  Found <TagAssign('x = x | strip | split: [...]', line 17, column 24)>", text)
    text = assert_in("  Closed node: NodeTag(assign)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 17, column 64)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 18, column: 5)", text)
    text = assert_in("  Found <TagEND('case', line 18, column 16)>", text)
    text = assert_in("  Closed node: NodeTag(endcase)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 18, column 19)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 19, column: 5)", text)
    text = assert_in("  Found <TagIncrement('x', line 19, column 18)>", text)
    text = assert_in("  Closed node: NodeTag(increment)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 19, column 22)>", text)
    text = assert_in("  Opened potential node: NodeTag (line: 20, column: 5)", text)
    text = assert_in("  Found <TagDecrement('y', line 20, column 18)>", text)
    text = assert_in("  Closed node: NodeTag(decrement)", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 20, column 22)>", text)
    text = assert_in("  Opened potential node: NodeOutput (line: 21, column: 5)", text)
    text = assert_in("  Found <TagOUTPUT('x', line 21, column 7)>", text)
    text = assert_in("  Closed node: OUTPUT", text)
    text = assert_in("  Found <TagLITERAL('\\n    ', line 21, column 10)>", text)
    text = assert_in("  END PARSING.", text)
    text = assert_in("- RENDERING <TagROOT('<string>::ROOT', line 1, column 1)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 1, column 1)>", text)
    text = assert_in("  Rendering <TagAssign('array = \"1,2,3,4,5\" | [...]', line 2, column 16)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 2, column 51)>", text)
    text = assert_in("  Rendering <TagCapture('x', line 3, column 17)>", text)
    text = assert_in("    Rendering <TagLITERAL('\\n        ', line 3, column 21)>", text)
    text = assert_in("    Rendering <TagFor('i in array reversed', line 4, column 17)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 4, column 39)>", text)
    text = assert_in("      Rendering <TagIf('forloop.index0 < 3', line 5, column 20)>", text)
    text = assert_in("        Rendering <TagLITERAL('\\n                ', line 5, column 41)>", text)
    text = assert_in("        Rendering <TagCycle('1, 2', line 6, column 27)>", text)
    text = assert_in("        Rendering <TagOUTPUT('i', line 6, column 36)>", text)
    text = assert_in("        Rendering <TagLITERAL(',\\n                ', line 6, column 39)>", text)
    text = assert_in("        Rendering <TagContinue('', line 7, column 29)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 7, column 32)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 4, column 39)>", text)
    text = assert_in("      Rendering <TagIf('forloop.index0 < 3', line 5, column 20)>", text)
    text = assert_in("        Rendering <TagLITERAL('\\n                ', line 5, column 41)>", text)
    text = assert_in("        Rendering <TagCycle('1, 2', line 6, column 27)>", text)
    text = assert_in("        Rendering <TagOUTPUT('i', line 6, column 36)>", text)
    text = assert_in("        Rendering <TagLITERAL(',\\n                ', line 6, column 39)>", text)
    text = assert_in("        Rendering <TagContinue('', line 7, column 29)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 7, column 32)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 4, column 39)>", text)
    text = assert_in("      Rendering <TagIf('forloop.index0 < 3', line 5, column 20)>", text)
    text = assert_in("        Rendering <TagLITERAL('\\n                ', line 5, column 41)>", text)
    text = assert_in("        Rendering <TagCycle('1, 2', line 6, column 27)>", text)
    text = assert_in("        Rendering <TagOUTPUT('i', line 6, column 36)>", text)
    text = assert_in("        Rendering <TagLITERAL(',\\n                ', line 6, column 39)>", text)
    text = assert_in("        Rendering <TagContinue('', line 7, column 29)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 7, column 32)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 4, column 39)>", text)
    text = assert_in("      Rendering <TagIf('forloop.index0 < 3', line 5, column 20)>", text)
    text = assert_in("      Rendering <TagElse('', line 8, column 21)>", text)
    text = assert_in("        Rendering <TagLITERAL('\\n                ', line 8, column 24)>", text)
    text = assert_in("        Rendering <TagBreak('', line 9, column 26)>", text)
    text = assert_in("        Rendering <TagLITERAL('\\n            ', line 9, column 29)>", text)
    text = assert_in("    Rendering <TagLITERAL('\\n    ', line 11, column 22)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 12, column 22)>", text)
    text = assert_in("  Rendering <TagCase('true', line 13, column 14)>", text)
    text = assert_in("    Rendering <TagLITERAL('\\n        ', line 13, column 21)>", text)
    text = assert_in("    Rendering <TagWhen('false', line 14, column 18)>", text)
    text = assert_in("    Rendering <TagElse('', line 16, column 17)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n            ', line 16, column 20)>", text)
    text = assert_in("      Rendering <TagAssign('x = x | strip | split: [...]', line 17, column 24)>", text)
    text = assert_in("      Rendering <TagLITERAL('\\n    ', line 17, column 64)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 18, column 19)>", text)
    text = assert_in("  Rendering <TagIncrement('x', line 19, column 18)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 19, column 22)>", text)
    text = assert_in("  Rendering <TagDecrement('y', line 20, column 18)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 20, column 22)>", text)
    text = assert_in("  Rendering <TagOUTPUT('x', line 21, column 7)>", text)
    text = assert_in("  Rendering <TagLITERAL('\\n    ', line 21, column 10)>", text)

def test_emptydrop():
    liq = Liquid('{% if object == empty %}{ \\\\{% endif %}')
    assert liq.render(object=[]) == '{ \\'

    liq = Liquid('{% if object != empty %}1{% endif %}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{% if object.empty? %}1{% endif %}')
    assert liq.render(object=[]) == '1'

    liq = Liquid('{{ object }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | reverse }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | sort }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | sort_natural }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | slice: 0 }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | uniq }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | join: "" }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | first }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{{ object | last }}')
    assert liq.render(object=[]) == ''

    liq = Liquid('{% if object %}1{% endif %}')
    assert liq.render(object=0.0) == '1'

    liq = Liquid('{% if empty %}1{% endif %}')
    assert liq.render() == ''
    liq = Liquid('{% if a["a"] %}1{% endif %}')
    assert liq.render(a={}) == ''

    liq = Liquid('{% unless object %}1{% endunless %}')
    assert liq.render(object=[]) == '1'

    liq = Liquid('{% unless empty %}1{% endunless %}')
    assert liq.render() == '1'

def test_output_newline():
    liq = Liquid('''abc
    {{- 123
    | no_such_filter -}}
    fff''', {'debug': True})
    with pytest.raises(LiquidRenderError) as exc:
        liq.render()
    assert "No such filter: 'no_such_filter'" in str(exc.value)
    assert "'<string> (abc {{- 123 | ...)', line 3, column 7" in str(exc.value)

def test_output_leading_newline():
    liq = Liquid('''abc
    {{-
    123 | no_such_filter -}}
    fff''', {'debug': True})
    with pytest.raises(LiquidRenderError) as exc:
        liq.render()
    assert "No such filter: 'no_such_filter'" in str(exc.value)
    assert "'<string> (abc {{- 123 | ...)', line 3, column 12" in str(exc.value)

def test_tag_leading_newline():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('''abc
        {%

        nosuchtag
        x %}
        fff''', {'debug': True})
    assert "No such tag:" in str(exc.value)
    assert "'<string> (abc {% nosuchtag ...)', line 4, column 9" in str(
        exc.value
    )

def test_unclosed_node():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('abc {%')
    assert 'Unclosed node NodeTag (<string>, line 1, column 5)' in str(
        exc.value
    )

def test_parent_tag_required():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% when %}')
    assert 'One of the parent tags is required' in str(exc.value)

def test_elder_tag_required():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% else %}')
    assert 'One of the elder tags is required' in str(exc.value)

def test_tag_check_elders():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% case 1 %}{% when 1 %}{%elsif 1%}{%endcase%}')
    assert "Tag 'elsif' expects elder tags" in str(exc.value)

def test_tag_check_parents():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% if 1 %}{% continue %}{% endif %}')
    assert "Tag 'continue' expects parents" in str(exc.value)

def test_tag_unclosed_inside():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% case 1 %}{% when 1 %}{%if 1%}{%endcase%}')
    assert "Tag unclosed: <TagIf" in str(exc.value)

def test_tag_unclosed_inside2():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% case 1 %}{% when 1 %}{%if 1%}{%endcase%}')
    assert "Tag unclosed: <TagIf" in str(exc.value)

def test_tag_parsed():
    liq = Liquid('abc')
    tag = liq.parsed.children[0]
    tag.parsed = ''
    assert tag.parsed == ''
    # revisit to trigger caching
    tag.parse()
    assert tag.parsed == ''

def test_lark_parser_error():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% capture 1 %}')
    assert 'Syntax error (<string>: line 1, column 12)' in str(exc.value)

def test_break_extra():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% for i in (1..3) %}{% break 1 %}{% endfor %}')

def test_empty_case():
    with pytest.raises(LiquidRenderError) as exc:
        Liquid('{% case 1 %}{% endcase %}').render()

def test_cycle_error():
    with pytest.raises(LiquidRenderError) as exc:
        Liquid('{% for i in (1..3) %}{% cycle a=1 %}{% endfor %}').render()
    with pytest.raises(LiquidRenderError) as exc:
        Liquid('{% for i in (1..3) %}{% cycle "group": 1, 2, 3 %}'
               '{% cycle "group": 1, 3 %}{% endfor %}').render()

def test_else_extra():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% if 1 %}{% else 2 %}{% endif %}').render()

def test_raw_extra():
    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid('{% raw 1 %}{% endraw %}').render()

def test_segment_repr():
    from liquid.tags.transformer import TagSegmentVar

    ts = TagSegmentVar('abc')
    assert repr(ts) == "<TagSegmentVar(data=('abc',))>"

def test_getattr_error():
    with pytest.raises(LiquidRenderError):
        Liquid('{{a.x}}').render(a={})

def test_range():
    assert Liquid('{{(a..b)}}').render(
        a=1, b=3
    )=='[1, 2, 3]'
