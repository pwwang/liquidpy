from liquid import Liquid


def test_shopify_case_and_alternate_not_equal(set_default_shopify):
    template = Liquid(
        "{% case value %}{% when 'bar', 'Hello' %}matched"
        "{% else %}no{% endcase %}|"
        "{% if value <> 'bar' %}different{% endif %}"
    )
    assert template.render(value="Hello") == "matched|different"


def test_shopify_tablerow_break_closes_cell(set_default_shopify):
    template = Liquid(
        "{% tablerow item in items %}{{ item }}{% break %}{% endtablerow %}"
    )
    assert template.render(items=[1, 2]) == (
        '<tr class="row1"><td class="col1">1</td></tr>'
    )


def test_shopify_inline_comment_ignores_tags(set_default_shopify):
    template = Liquid(
        "{% inline_comment %}{% unknown %}{% endinline_comment %}visible"
    )
    assert template.render() == "visible"


def test_shopify_capture_and_loop_assignment(set_default_shopify):
    template = Liquid(
        "{% capture value %}{% decrement counter %}{% endcapture %}"
        "{{ value }}|{% assign seen = '' %}"
        "{% for item in items %}{% assign seen = item %}{% endfor %}{{ seen }}"
    )
    assert template.render(items=["last"]) == "-1|last"
