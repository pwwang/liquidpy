"""Just add tests for the codes that are not covered by other tests"""
import pytest
from liquid import Liquid
from liquid.exceptions import (
    EndTagUnexpected,
    TagUnclosed,
    TagSyntaxError,
    LiquidRenderError,
    TagWrongPosition
)

def test_endtagunexpected():
    with pytest.raises(EndTagUnexpected):
        Liquid("{% endif %}")

def test_child_unclosed():
    with pytest.raises(TagUnclosed):
        Liquid("{% for i in (1..2) %}{% if i == 1 %}{{i}}{%else%}{% endfor %}")

def test_child_unclosed_2():
    with pytest.raises(TagUnclosed):
        # if not closed
        Liquid("{% capture x %}{% if i == 1 %}{{i}}{%else%}{% endfor %}")

def test_child_unclosed_3():
    with pytest.raises(EndTagUnexpected):
        # if not closed
        Liquid("{% case true %}{% when true %}{% endx %}")

def test_child_unclosed_4():
    with pytest.raises(TagUnclosed):
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
    rendered = Liquid(tpl, liquid_config={'debug':'plus'}).render()
    assert rendered == """
    0
    -1
    15,24,13,
    """
    assert ": <Tag(name=capture, line=3, col=9, VOID=False)>" in caplog.text
    assert ":   <Tag(name=for, line=4, col=13, VOID=False)>" in caplog.text
    assert ":     <Tag(name=if, line=5, col=17, VOID=False)>" in caplog.text
    assert ":       <Tag(name=cycle, line=6, col=21, VOID=True)>" in caplog.text
    assert ":       <Tag(name=continue, line=7, col=21, VOID=True)>" in caplog.text
    assert ":     <Tag(name=else, line=8, col=17, VOID=False)>" in caplog.text
    assert ":       <Tag(name=break, line=9, col=21, VOID=True)>" in caplog.text
    assert ": <Tag(name=case, line=13, col=9, VOID=False)>" in caplog.text
    assert ":   <Tag(name=when, line=14, col=13, VOID=False)>" in caplog.text
    assert ":   <Tag(name=else, line=16, col=13, VOID=False)>" in caplog.text

def test_when():
    tpl = """
    {%case true%}
        {%when false%}
        abc
    {%endcase%}
    """
    assert Liquid(tpl).render().strip() == ''

def test_unless():
    tpl = """
    {% unless x %}
    123
    {% endunless %}
    """
    assert Liquid(tpl).render(x="").strip() == ''
    assert Liquid(tpl).render(x=0).strip() == ''
    # EmptyDrop
    assert Liquid(tpl).render(x=[]).strip() == '123'
    tpl = """
    {% unless x %}
    123
    {% else %}
    empty
    {% endunless %}
    """
    assert Liquid(tpl).render(x="").strip() == 'empty'

def test_if():
    tpl = """
    {% if x %}
    123
    {% endif %}
    """
    assert Liquid(tpl).render(x="").strip() == '123'
    assert Liquid(tpl).render(x=0).strip() == '123'
    # EmptyDrop
    assert Liquid(tpl).render(x=[]).strip() == ''

def test_cycle_different_args():
    tpl = """
    {% for i in (1..2) %}
    {% cycle "group": 1,2,3 %}
    {% cycle "group": 2,3,4 %}
    {% endfor %}
    """
    with pytest.raises(LiquidRenderError) as lre:
        Liquid(tpl).render()
    assert '[ValueError]' in str(lre)

def test_empty_case():
    tpl = """
    {% case 1 %}
    {% endcase %}
    """
    with pytest.raises(TagSyntaxError):
        Liquid(tpl).render()

def test_render_error():
    tpl = """
    {% if x %}
        {{x.b}}
    {% endif %}
    """
    with pytest.raises(LiquidRenderError) as lre:
        Liquid(tpl).render(x={'a':1})

    assert '[AttributeError]' in str(lre)

def test_no_such_filter():
    tpl = "{{1 | nosuchfilter}}"

    with pytest.raises(LiquidRenderError) as lre:
        Liquid(tpl).render()

    assert 'No such filter' in str(lre)

def test_getitem_emptydrop():
    tpl = "{{x['b']}}"
    assert Liquid(tpl).render(x={}) == ''

def test_no_parent():
    tpl = "{% when true %}"
    with pytest.raises(TagWrongPosition) as twp:
        Liquid(tpl)
    assert "Expecting parents ('case',)" in str(twp)
