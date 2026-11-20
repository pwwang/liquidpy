import asyncio

from liquid import Liquid


def test_shopify_relational_comparisons_and_nested_branches(set_default_shopify):
    template = Liquid(
        "{% if 1 < 2 and 2 <= 2 and 3 > 2 and 3 >= 3 %}ordered{% endif %}"
        "|{% if nil < 1 or blank > 1 or true < 2 or 1 < 'a' %}bad{% endif %}"
        "|{% if true %}{% if true %}  {% endif %}{% endif %}"
        "{% if true %}{% assign value = 2 %}{% endif %}{{ value }}"
        "|{% if true %}{% if true %}{{ value }}{% endif %}{% endif %}"
    )
    assert template.render() == "ordered||2|2"


def test_shopify_context_wrapping_in_sync_and_async_renders(set_default_shopify):
    sync_template = Liquid("{{ data.name }}", mode="shopify")
    assert sync_template.render({"data": {"name": "sync"}}) == "sync"

    async_template = Liquid(
        "before\r{{ values[0].name }}\r",
        mode="shopify",
        enable_async=True,
    )
    assert asyncio.run(
        async_template.render_async(values=({"name": "async"},))
    ) == "before\rasync\r"


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
    template = Liquid(
        "{% tablerow item in items %}{% if item == 1 %}{% break %}"
        "{% endif %}{{ item }}{% endtablerow %}"
    )
    assert template.render(items=[1, 2]) == (
        '<tr class="row1">\n<td class="col1"></td></tr>\n'
    )
    template = Liquid(
        "{% tablerow item in items %}{% if item == 1 %}{{ item }}"
        "{% elsif item == 2 %}{% break %}{% else %}other{% endif %}"
        "{% endtablerow %}"
    )
    assert template.render(items=[1, 2]) == (
        '<tr class="row1">\n<td class="col1">1</td>'
        '<td class="col2"></td></tr>\n'
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
