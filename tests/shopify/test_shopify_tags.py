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
        '<tr class="row1">\n<td class="col1">1</td></tr>\n'
    )
    template = Liquid(
        "{% tablerow item in items cols: 2 %}{{ item }}{% break %}"
        "{% endtablerow %}"
    )
    assert template.render(items=[1, 2, 3]) == (
        '<tr class="row1">\n<td class="col1">1</td></tr>\n'
    )


def test_shopify_inline_comment_ignores_tags(set_default_shopify):
    template = Liquid(
        "{% inline_comment %}{% unknown %}{% endinline_comment %}visible"
    )
    assert template.render() == "visible"


def test_shopify_inline_comment_syntax(set_default_shopify):
    template = Liquid("{%- # {% echo 'hello world' %} -%}")
    assert template.render() == " -%}"


def test_shopify_nested_comments(set_default_shopify):
    template = Liquid(
        "{% comment %}    {% comment %}    {% comment %}"
        "{%    endcomment     %}    {% endcomment %}{% endcomment %}"
    )
    assert template.render() == ""


def test_shopify_whitespace_only_branches(set_default_shopify):
    template = Liquid(
        "{% if true %}  {% elsif false %} {% else %} {% endif %}"
        "|{% unless false %}  {% endunless %}"
    )
    assert template.render() == "|"


def test_shopify_whitespace_control_preserves_carriage_return(set_default_shopify):
    template = Liquid(
        "\r{% if customer -%}\rWelcome back,  "
        "{{ customer.first_name -}} !\r {%- endif -%}"
    )
    assert template.render(customer={"first_name": "Holly"}) == (
        "\rWelcome back,  Holly!"
    )


def test_shopify_capture_and_loop_assignment(set_default_shopify):
    template = Liquid(
        "{% capture value %}{% decrement counter %}{% endcapture %}"
        "{{ value }}|{% assign seen = '' %}"
        "{% for item in items %}{% assign seen = item %}{% endfor %}{{ seen }}"
    )
    assert template.render(items=["last"]) == "-1|last"


def test_shopify_capture_assign(set_default_shopify):
    template = Liquid(
        "{% capture x %}{% assign y = 2 %}{% endcapture %}[{{ x }}{{ y }}]"
    )
    assert template.render() == "[2]"
