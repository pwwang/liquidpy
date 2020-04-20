import sys
from pathlib import Path
import pytest
from diot import Diot
import liquid
from liquid import Liquid, LiquidSyntaxError, LiquidRenderError

HERE = Path(__file__).parent.resolve()

@pytest.fixture(scope = "function")
def debug_on():
    dbg = Liquid.debug()
    Liquid.debug(True)
    yield
    Liquid.debug(dbg)

@pytest.fixture(scope = "function")
def debug_off():
    dbg = Liquid.debug()
    Liquid.debug(False)
    yield
    Liquid.debug(dbg)

@pytest.mark.parametrize('text, data, out', [
    ('{% if 1%}{%endif%}', {}, ''),
    ('{{ page.title }}', {'page': dict(title = 'Introduction')}, 'Introduction'),
    ('''{% if user %}\nHello {{ user.name }}!{% endif %}''', {'user': dict(name = 'Adam')}, '\nHello Adam!'),
    ('''{% if `product.title` == "Awesome Shoes" %}
  These shoes are awesome!{% endif %}''', {'product': dict(title = 'Awesome Shoes')}, '\n  These shoes are awesome!'),
    ('''{% if `product.type` == "Shirt" or `product.type` == "Shoes" %}
  This is a shirt or a pair of shoes.{% endif %}''', {'product': dict(type = 'Shirt')}, '''\n  This is a shirt or a pair of shoes.'''),
        # python 'in' used instead of liquid 'contains'
    ('''{% if 'Pack' in `product.title` %}
  This product's title contains the word Pack.{% endif %}''', {'product': dict(title = 'whateverPack')}, '\n  This product\'s title contains the word Pack.'),
    ('''{% if 'Hello' in `product.tags` %}
  This product has been tagged with 'Hello'.{% endif %}''', {'product': dict(tags = '23Hello234')}, "\n  This product has been tagged with 'Hello'."),

    ('''{% assign tobi = "Tobi" %}

{% if tobi %}
  This condition will always be true.
{% endif %}''', {}, '''\n\n
  This condition will always be true.
'''),

        # different truthy from liquid
        # see: https://shopify.github.io/liquid/basics/truthy-and-falsy/
    ('''{% if `settings.fp_heading` -%}
  <h1>{{ settings.fp_heading }}</h1>{% endif %}''', {'settings': dict(fp_heading = 1)}, '  <h1>1</h1>'),
])
def test_render_0(text, data, out):
    l = Liquid(text, liquid_loglevel='debug')
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('{% assign my_string = "Hello World!" %}{{my_string}}', {}, 'Hello World!'),
    ('{% assign my_int = 25 %}{{my_int}}', {}, '25'),
        # 10
    ('{% assign my_float = 39.756 %}{{my_float}}', {}, '39.756'),
    ('{% assign foo = true %}{% if foo %}true{% else %}false{% endif %}', {}, 'true'),
    ('{% assign foo = false %}{% if foo %}true{% else %}false{% endif %}', {}, 'false'),
    ('{% assign foo = nil %}{% if foo %}true{% else %}false{% endif %}', {}, 'false'),

        # whitespace controls
    ('''{% mode loose -%}
{% assign my_variable = "tomato" %}
{{ my_variable }}''', {}, '''
tomato'''),
    ('''{% mode loose %}
{%- assign my_variable = "tomato" -%}
{{ my_variable }}''', {}, 'tomato'),
    ('''{% assign username = "John G. Chalmers-Smith" -%}
{% if username and len(username) > 10 -%}
  1Wow, {{ username }}, you have a long name!
{%- else %}
  Hello there!
{% endif %}
''', {}, '  1Wow, John G. Chalmers-Smith, you have a long name!\n'),
    ('''{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and len(username) > 10 -%}
  2Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif %}
''', {}, '  2Wow, John G. Chalmers-Smith, you have a long name!\n'),

        # comments
    ('''Anything you put between {% comment %}and {% endcomment %} tags
is turned into a comment.''', {}, '''Anything you put between # and  tags
is turned into a comment.'''),
    ('''Anything you put between {# and #} tags
is turned into a comment.''', {}, '''Anything you put between  tags
is turned into a comment.'''),
])
def test_render_1(text, data, out):
    l = Liquid(text, liquid_loglevel='debug')
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
        #20
        # unless
    ('''{% unless `product.title` == 'Awesome Shoes' %}
  These shoes are not awesome.
{% endunless %}''', {'product': dict(title = 'Notawesome Shoes')}, '''\n  These shoes are not awesome.
'''),
        # elsif
    ('''{% if `customer.name` == 'kevin' %}
  Hey Kevin!
{% elsif `customer.name` == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': dict(name = 'anonymous')}, '''\n  Hey Anonymous!
'''),
    ('''{% if `customer.name` == 'kevin' %}
  Hey Kevin!
{% elseif `customer.name` == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': dict(name = 'anonymous')}, '''\n  Hey Anonymous!
'''),
    ('''{% if `customer.name` == 'kevin' %}
  Hey Kevin!
{% else if `customer.name` == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': dict(name = 'anonymous')}, '''\n  Hey Anonymous!
'''),

        # case / when
    ('''{% assign handle = 'cake' %}
{% case handle %}
  {% when 'cake' %}
     This is a cake
  {% when 'cookie' %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}{%if 1%}1{%endif%}''', {}, '''\n\n  \n     This is a cake\n  1'''),

    ('''{% for product in `collection.products` %}
{{ product.title }}
{% endfor %}''', {'collection': dict(
    products = [
        dict(title = 'hat'),
        dict(title = 'shirt'),
        dict(title = 'pants')
    ])}, '''\nhat

shirt

pants
'''),

    ('''{% for i in range(1, 6): %}
  {% if i == 4: %}
    {% break %}
  {% else: %}
    {{ i }}
  {% endif %}
{% endfor %}''', {}, '''\n  \n    1\n  \n\n  \n    2\n  \n\n  \n    3\n  \n\n  \n    '''),

    ('''{% for i in range(1, 6) %}
  {% if i == 4 %}
    {% continue %}
  {% else %}
    {{ i }}
  {% endif %}
{% endfor %}''', {}, '''\n  \n    1\n  \n\n  \n    2\n  \n\n  \n    3\n  \n\n  \n    \n  \n    5\n  \n'''),

])
def test_render_2(text, data, out, debug_on):
    l = Liquid(text, liquid_loglevel='debug')
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('''raw:
    {%- raw -%}
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
{%- endraw %}''', {}, '''raw:  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.'''),
        # assign
    ('''{% assign my_variable = false %}
{% if my_variable != true %}
  This statement is valid.
{% endif %}''', {}, '\n\n  This statement is valid.\n'),
    ('''{% assign foo = "bar" %}
{{ foo }}''', {}, '''\nbar'''),

        # capture
    ('''{% capture my_variable %}I am being captured.{% endcapture %}
{{ my_variable }}''', {}, '\nI am being captured.'),

        # capture
    ('''{% assign favorite_food = 'pizza' %}
{% assign age = 35 %}

{% capture about_me %}
I am {%if age == 35%}{{ age }}{%endif%} and my favorite food is {{ favorite_food }}.
{% endcapture %}

{{ about_me }}''', {}, '\n\n\n\n\n\nI am 35 and my favorite food is pizza.\n'),

        # in/decrement
    ('''{% increment my_counter %}
        {{ my_counter }}
        {% increment my_counter %}
        {{ my_counter }}
        {% increment my_counter %}
        {{ my_counter }}''', {'my_counter': 0}, '''\n        1\n        \n        2\n        \n        3''' ),

    ('''{% decrement my_counter %}
        {{ my_counter }}
        {% decrement my_counter %}
        {{ my_counter }}
        {% decrement my_counter %}
        {{ my_counter }}''', {'my_counter': 0}, '''\n        -1\n        \n        -2\n        \n        -3''' ),

        # filters
    ('{{ -17 | @abs }}', {}, '17'),
    ('{{ 4 | @abs }}', {}, '4'),
    ('{{ "-19.86" | @abs }}', {}, '19.86'),
    ('{{ "/my/fancy/url" | @append: ".html" }}', {}, '/my/fancy/url.html'),
    ('{% assign filename = "/index.html" %}{{ "website.com" | @append: filename }}', {}, 'website.com/index.html'),
    ('{{ "adam!" | @capitalize | @prepend: "Hello " }}', {}, 'Hello Adam!'),
    ('{{ 4 | @at_least: 5 }}', {}, '4'),
    ('{{ 4 | @at_least: 3 }}', {}, '3'),
    ('{{ 4 | @at_most: 5 }}', {}, '5'),
    ('{{ 4 | @at_most: 3 }}', {}, '4'),
    ('{{ "title" | @capitalize }}', {}, 'Title'),
    ('{{ "my great title" | @capitalize }}', {}, 'My great title'),
])
def test_render_3(text, data, out):
    l = Liquid(text, liquid_loglevel='debug')
    #print(repr( l.render(**data)))
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('''{% assign site_categories = `site.pages | @map: 'category'` %}

{% for category in site_categories %}
  {{ category }}
{% endfor %}''', {'site': dict(pages = [
    dict(category = 'business'),
    dict(category = 'celebrities'),
    dict(category = ''),
    dict(category = 'lifestyle'),
    dict(category = 'sports'),
    dict(category = ''),
    dict(category = 'technology')
])}, '''\n\n\n  business\n\n  celebrities\n\n  \n\n  lifestyle\n\n  sports\n\n  \n\n  technology\n'''),
    ('''{% assign site_categories = `site.pages | @map: 'category' | @compact` %}

{% for category in site_categories %}
  {{ category }}
{% endfor %}''', {'site': dict(pages = [
    dict(category = 'business'),
    dict(category = 'celebrities'),
    dict(category = ''),
    dict(category = 'lifestyle'),
    dict(category = 'sports'),
    dict(category = ''),
    dict(category = 'technology')
])}, '''\n\n\n  business\n\n  celebrities\n\n  lifestyle\n\n  sports\n\n  technology\n'''),
    ('''{% assign fruits = `"apples, oranges, peaches" | @split: ", "` %}
{% assign vegetables = `"carrots, turnips, potatoes" | @split: ", "` %}

{% assign everything = `fruits | @concat: vegetables` %}
{% for item in everything %}
- {{ item }}
{% endfor %}''', {}, '''\n\n\n\n\n- apples\n\n- oranges\n\n- peaches\n\n- carrots\n\n- turnips\n\n- potatoes\n'''),
    ('''{% assign furniture = `"chairs, tables, shelves" | @split: ", "` %}

{% assign everything = `fruits | @concat: vegetables | @concat: furniture` %}
{% for item in everything %}
- {{ item }}
{% endfor %}''', {'fruits': "apples, oranges, peaches".split(", "), 'vegetables': "carrots, turnips, potatoes".split(', ')}, '''\n\n\n\n- apples\n\n- oranges\n\n- peaches\n\n- carrots\n\n- turnips\n\n- potatoes\n\n- chairs\n\n- tables\n\n- shelves\n'''),
])
def test_render_4(text, data, out):
    l = Liquid(text)
    #print(repr( l.render(**data)))
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('{{ article.published_at | @date: "%a, %b %d, %y", "%m/%d/%Y" }}', {'article': dict(published_at = '07/17/2015')}, 'Fri, Jul 17, 15'),
    ('{{ article.published_at | @date: "%Y", "%m/%d/%Y" }}', {'article': dict(published_at = '07/17/2015')}, '2015'),
    ('{{ "March 14, 2016" | @date: "%b %d, %y", "%B %d, %Y" }}', {}, 'Mar 14, 16'),
    ('This page was last updated at {{ "now" | @date: "%Y-%m-%d %H" }}.', {}, 'This page was last updated at {}.'.format(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H"))),
    ('This page was last updated at {{ "today" | @date: "%Y-%m-%d %H" }}.', {}, 'This page was last updated at {}.'.format(__import__('datetime').datetime.today().strftime("%Y-%m-%d %H"))),

    ('{{ product_price | @default: 2.99 }}', {'product_price': None}, '2.99'),
    ('{{ product_price | @default: 2.99 }}', {'product_price': 4.99}, '4.99'),
    ('{{ product_price | @default: 2.99 }}', {'product_price': ''}, '2.99'),

    ('{{ 16 | @divided_by: 4 | int }}', {}, '4'),  # 'python 3 returns 4.0 anyway'
    ('{{ 5 | @divided_by: 3 | int }}', {}, '1'),
    ('{{ 20 | @divided_by: 7 | int }}', {}, '2'),
    ('{{ 20 | @divided_by: 7.0 | str | [:5] }}', {}, '2.857'),

    ('{{ "Parker Moore" | @downcase }}', {}, 'parker moore'),
    ('{{ "apple" | @downcase }}', {}, 'apple'),

    ('''{{ "Have you read 'James & the Giant Peach'?" | @escape }}''', {}, 'Have you read \'James &amp; the Giant Peach\'?'),
    ('{{ "Tetsuro Takara" | @escape }}', {}, 'Tetsuro Takara'),

    ('{{ 1.2 | @floor | int }}', {}, '1'), # '1.0' in python
    ('{{ 2.0 | @floor | int }}', {}, '2'),
    ('{{ 183.357 | @floor | int }}', {}, '183'),
    ('{{ "3.5" | @floor | int }}', {}, '3'),

    ('''{% assign beatles = `"John, Paul, George, Ringo" | @split: ", "` %}

{{ beatles | @join: " and " }}''', {}, '''\n\nJohn and Paul and George and Ringo'''),

    ('{{ "          So much room for activities!          " | @lstrip }}', {}, "So much room for activities!          "),
])
def test_render_5(text, data, out):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('{{ 4 | @minus: 2 }}', {}, '2'),
    ('{{ 16 | @minus: 4 }}', {}, '12'),
    ('{{ 183.357 | @minus: 12 }}', {}, '171.357'),
    ('{{ 3 | @modulo: 2 }}', {}, '1'),
    ('{{ 24 | @modulo: 7 }}', {}, '3'),
    ('{{ 183.357 | @modulo: 12 | round: 3 }}', {}, '3.357'),
    ('{{ 4 | @plus: 2 }}', {}, '6'),
    ('{{ 16 | @plus: 4 }}', {}, '20'),
    ('{{ 183.357 | @plus: 12 }}', {}, '195.357'),

        # 81
    ('''{% capture string_with_newlines %}
Hello
there
{% endcapture %}
{{ string_with_newlines | @newline_to_br }}''', {}, '''\n<br />Hello<br />there<br />'''),

    ('{{ "apples, oranges, and bananas" | @prepend: "Some fruit: " }}', {}, 'Some fruit: apples, oranges, and bananas'),
    ('''{% assign url = "liquidmarkup.com" %}

{{ "/index.html" | @prepend: url }}''', {}, '''\n\nliquidmarkup.com/index.html'''),

    ('{{ "I strained to see the train through the rain" | @remove: "rain" }}', {}, 'I sted to see the t through the '),
        # 85
    ('{{ "I strained to see the train through the rain" | @remove_first: "rain" }}', {}, 'I sted to see the train through the rain'),

    ('{{ "Take my protein pills and put my helmet on" | @replace: "my", "your" }}', {}, 'Take your protein pills and put your helmet on'),
    ('{{ "Take my protein pills and put my helmet on" | @replace_first: "my", "your" }}', {}, 'Take your protein pills and put my helmet on'),

    ('''
{% assign my_array = `"apples, oranges, peaches, plums" | @split: ", "` %}

{{ my_array | @reverse | @join: ", " }}''', {}, '''\n\n\nplums, peaches, oranges, apples'''),

    ('{{ "Ground control to Major Tom." | @split: "" | @reverse | @join: "" }}', {}, '.moT rojaM ot lortnoc dnuorG'),

    ('{{ 1.2 | @round }}', {}, '1.0'),
    ('{{ 2.7 | @round }}', {}, '3.0'),
        #92
    ('{{ 183.357 | @round: 2 }}', {}, '183.36'),

    ('{{ "          So much room for activities!          " | @rstrip }}', {}, '          So much room for activities!'),
    ('{{ "          So much room for activities!          " | @strip }}', {}, 'So much room for activities!'),

    ('{{ "Ground control to Major Tom." | @size }}', {}, '28'),
    ('{% assign my_array = `"apples, oranges, peaches, plums" | @split: ", "` %}{{ my_array | @size }}', {}, '4'),

    ('{{ "Liquid" | @slice: 0 }}', {}, 'L'),
    ('{{ "Liquid" | @slice: 2 }}', {}, 'q'),
        # 99
    ('{{ "Liquid" | @slice: 2, 5 }}', {}, 'quid'),
    ('{{ "Liquid" | @slice: -3, 2 }}', {}, 'ui'),

    ('{% assign my_array = `"zebra, octopus, giraffe, Sally Snake" | @split: ", "` %}{{ my_array | @sort | @join: ", " }}', {}, 'Sally Snake, giraffe, octopus, zebra'),
])
def test_render_6(text, data, out):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('''{% assign beatles = `"John, Paul, George, Ringo" | @split: ", "` %}

{% for member in beatles %}
  {{ member }}
{% endfor %}''', {}, '''\n\n
  John\n
  Paul\n
  George\n
  Ringo
'''),
    ('{{ "Have <em>you</em> read <strong>Ulysses</strong>?" | @strip_html }}', {}, 'Have you read Ulysses?'),
        #104
    ('''{% capture string_with_newlines %}
Hello
there
{% endcapture %}
{{ string_with_newlines | @strip_newlines }}''', {}, '\nHellothere',),

    ('{{ 3 | @times: 2 }}', {}, '6'),
    ('{{ 24 | @times: 7 }}', {}, '168'),
    ('{{ 183.357 | @times: 12 }}', {}, '2200.284'),

    ('{{ "Ground control to Major Tom." | @truncate: 20 }}', {}, 'Ground control to...'),
        # 109
    ('{{ "Ground control to Major Tom." | @truncate: 25, ", and so on" }}', {}, 'Ground control, and so on'),
    ('{{ "Ground control to Major Tom." | @truncate: 20, "" }}', {}, 'Ground control to Ma'),

    ('{{ "Ground control to Major Tom." | @truncatewords: 3 }}', {}, 'Ground control to...'),
    ('{{ "Ground control to Major Tom." | @truncatewords: 3, "--" }}', {}, 'Ground control to--'),
    ('{{ "Ground control to Major Tom." | @truncatewords: 3, "" }}', {}, 'Ground control to'),
    ('{{ "Gro" | @truncatewords: 3 }}', {}, 'Gro'),

    ('''{% assign my_array = `"ants, bugs, bees, bugs, ants" | @split: ", "` -%}
{{ my_array | @uniq | @sort | @join: ", " }}''', {}, 'ants, bees, bugs'),

    ('{{ "Parker Moore" | @upcase }}', {}, 'PARKER MOORE'),
    ('{{ "APPLE" | @upcase }}', {}, 'APPLE'),
        # 117
    ('{{ "%27Stop%21%27+said+Fred" | @url_decode }}', {}, "'Stop!'+said+Fred"),
    ('{{ "john@liquid.com" | @url_encode }}', {}, 'john%40liquid.com'),
    ('{{ "Tetsuro Takara" | @url_encode }}', {}, 'Tetsuro+Takara'),
        # while
    ('''{% while True %}
{% increment a %}
{{a}}
{% if a == 3 %}{% break %}{% endif %}
{% endwhile %}''', {'a':0}, '''\n\n1\n\n\n\n2\n\n\n\n3\n'''),
        # python
    ('''{% import os %}
{{os.path.basename('a/b/c')}}''', {}, '\nc'),
])
def test_render_7(text, data, out):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
        # raw
    ('''{% raw %}
whatever
I{% if %}
enter{% comment %}
here{% raw %}
is preversed
{% endraw %}''', {}, '''
whatever
I{% if %}
enter{% comment %}
here{% raw %}
is preversed
'''),
    ('''{% comment %}
whatever
I{% if c%}
enter{{ comment }}
here{% endif %}
is treated as comments
{% endcomment %}''', {'c': True, 'comment': 'comment'}, '''# \n# whatever
# I
# entercomment
# here
# is treated as comments
'''),
    ('''{% mode compact %}{% capture a %}
{% for i in range(5) %}
    {% if i == 2 %}
        {% continue %}
    {% endif %}
{{i}}{% endfor %}
{% endcapture %}
{{a}}''', {}, '0134'),
    ('{{len("123") | @plus: 3}}', {}, '6'),
        # 126
    ('{{1.234, 1+1 | *round }}', {}, '1.23'),
    ('{{1.234 | round: 2 }}', {}, '1.23'),
    ('{{ [1,2,3] | [0] }}', {}, '1'),
    ('{{ [1,2,3] | [1:] | sum }}', {}, '5'),
    ('{{ {"a": 1} | ["a"] }}', {}, '1'),
        # 131
    ('{{ "," | .join: ["a", "b"] }}', {}, 'a,b'),
    ('{{ 1.234, 1+1 | [1] }}', {}, '2'),
    ('{{ "/path/to/file.txt" | :len(_) - 4 }}', {}, '13'),
])
def test_render_8(text, data, out):
    l = Liquid(text, liquid_loglevel='debug')
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
    ('{{ "{}, {}!" | .format: "Hello", "world" }}', {}, 'Hello, world!'),
    ('''{% mode compact %}
{% from os import path %}
{{ "/path/to/file.txt" | lambda p: path.join( path.dirname(p), path.splitext(p)[0] + '.sorted' + path.splitext(p)[1] ) }}''', {}, '/path/to/file.sorted.txt'),
    ("{{ '1' | .isdigit() }}", {}, 'True'),
        # 137
    ("{{ '1' | .isdigit: }}", {}, 'True'),
    ("{{ x | ['a']: 1, 2 }}", {'x': {'a': lambda x, y: x+y}}, '3'),
    ("{{ x | ['a'] }}", {'x': {'a': 1}}, '1'),
        # 140
    ("{{ x | ['a']: }}", {'x': {'a': lambda: 2}}, '2'),
    ("{{ x | ['a']() }}", {'x': {'a': lambda: 2}}, '2'),
    ('''{% comment # -%}
a
b
c
{% endcomment %}''', {}, '''# a
# b
# c
'''),
    ('''{% comment /* */ -%}
a
b
c
{%- endcomment %}''', {}, '''/* a */
/* b */
/* c */'''),
        # 144
    #("{{ x | ifelse: (lambda a: isinstance(a, list)), (lambda b: [b]), None | [0] | sum }}", {'x': [1,2,3]}, '6'),
    ("{{ x | @append: '.html' | len }}", {'x': 'test'}, '9'),
    ("{{ x | : _, _ + '.html' | *lambda _1, _2:_1+_2 }}", {'x': 'test'}, 'testtest.html'),

        # 147
        # {{ x | @filter }} => filter(x)
    ("{{ -1 | @abs}}", {}, '1'),
        # {{ x | @filter: a }} => filter(x, a)
    ("{{ 183.357 | @round: 2}}", {}, '183.36'),
        # {{ x, y | *@filter: a }} => filter(x, y, a)
    ("{{ 'a,b,c,d', ',' | *@replace: '|' }}", {}, "a|b|c|d"),

        # 150
        # {{ x, y | @filter: a }} => filter((x, y), a)
    ("{{ 1,2 | @concat: (3,4) | sum}}", {}, '10'),
    ("{{ 1,2 | :_ + (3,4) | sum}}", {}, '10'),
        # {{ x, y | *&@filter: a }} => (x, y, filter(x, y, a))
    ("{{ 'a,b,c,d', ',' | *@replace: '|' | @split: '|' | :'-'.join(_) }}", {}, 'a-b-c-d'),
        # {{ x, y | &@filter: a }} => (x, y, filter((x, y), a))
    ("{{ 1,2 | @concat: (3,4) }}", {}, '(1, 2, 3, 4)'),
    ("{{ 'a/b/c.txt' | Path | .name }}", {'Path': __import__('pathlib').Path}, 'c.txt'),
    ("{{ 'a/b/c.txt' | Path | .is_file: }}", {'Path': __import__('pathlib').Path}, 'False'),
    ("""{%- from pathlib import Path -%}
{{- filepath | ? | = Path | .name | str |
              ! : _ | @append: "empty.file" |
              $ Path | .suffix  -}}
""", {"filepath": ""}, ".file"),
    ("""{%- from pathlib import Path -%}
{{- filepath | ? | = Path | .name | str |
              ! : _ | @append: "empty.file" |
              $ Path | .suffix  -}}
""", {"filepath": "/a/b/c.txt"}, ".txt"),
])
def test_render_9(text, data, out):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
        # 154
        # {{ x | .__file__}} => x.__file__
    ("{{module | .__file__}}", {'module': pytest}, pytest.__file__),
        # {{ x | .join(["a", "b"]) }} => x.join(["a", "b"])
    ("{{',' | .join(['a', 'b']) }}", {}, 'a,b'),
        # {{ x | .join: ["a", "b"]}} => x.join(["a", "b"])
    ("{{',' | .join: ['a', 'b'] }}", {}, 'a,b'),
        # {{ x | &.attr }} => (x, x.attr)
    ("{{'a' | .isupper()}}", {}, "False"),
        # {{ x, y | .count(1) }} => (x, y).count(1)
    ("{{ 1,2 | .count(1) }}", {}, '1'),
        # {{ x, y | .count: 1 }} => (x, y).count(1)
    ("{{ 1,2 | .count: 2 }}", {}, '1'),

        # 160
        # {{ x, y | *.join: ["a", "b"] }} => x.join(["a", "b"]) # y lost!!
    ("{{ ',' | .join: ['a', 'b']}}", {}, 'a,b'),
        # {{ x, y | &.count:1 }} => (x, y, (x, y).count(1))
    ("{{ 1,2 | .count: 2 }}", {}, '1'),
        # {{ x, y | *&.join: ["a", "b"] }} => (x, y, x.join(["a", "b"]))
    ("{{ '.' | .join: ['a', 'b']}}", {}, "a.b"),

        # 163
        # {{ x | [0] }} => x[0]
    ("{{[1,2] | [0]}}", {}, '1'),
        # {{ x | &[0] }} => (x, x[0])
    ("{{[1,2] | [1]}}", {}, '2'),
        # {{ x | [0](1) }} => x[0](1)
    ("{{[lambda a: a*10,2] | [0](1) }}", {}, '10'),
        # {{ x | [0]: 1 }} => x[0](1)
    ("{{[lambda a: a*10,2] | [0]: 1 }}", {}, '10'),
        # {{ x, y | [0] }} => (x, y)[0] == x
    ("{{ [1,2], 3 | [0] }}", {}, '[1, 2]'),
        # {{ x, y | *[0] }} => x[0]
    ("{{ [1,2], 3 | [0][0] }}", {}, '1'),
        # {{ x, y | &[0] }} => (x, y, (x, y)[0]) == (x, y, x)
    #("{{ [1,2], 3 | [0] }}", {}, '([1, 2], 3, [1, 2])'),

        # 170
        # {{ x, y | *&[0] }} => (x, y, x[0])
    ("{{ [1,2], 3 | [0][1] }}", {}, '2'),
        # {{ x, y | [0]: 1 }} => (x, y)[0](1)
    ("{{lambda a: a*10, 2 | [0]: 1 }}", {}, '10'),

        # 172
        # {{ x | :a[1]}} => (lambda a: a[1])(x)
    ("{{[1,2] | :_[1]}}", {}, '2'),
        # {{ x | &:a[1] }} => (x, (lambda a: a[1])(x))
    ("{{[1,2] | :_, _[1]}}", {}, '([1, 2], 2)'),
        # {{ x, y | *:a+b }} => (lambda a, b: a+b)(x, y)
    ("{{1, 2 | *lambda _1,_2:_1+_2}}", {}, '3'),
        # {{ x, y | :sum(a)}} => (lambda a: sum(a))((x, y))
    ("{{1, 2 | :sum(_)}}", {}, '3'),
])
def test_render_10(text, data, out):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
        # 176 real lambda
        # {{ x | lambda a:a[1]}} => (lambda a: a[1])(x)
    ("{{ 1 | lambda a: a*10}}", {}, '10'),
        # {{ x | &lambda a:a[1] }} => (x, (lambda a: a[1])(x))
    ("{{ 1 | lambda a: a, a*10}}", {}, '(1, 10)'),
        # {{ x, y | *lambda a, b: a+b }} => (lambda a, b: a+b)(x, y)
    ("{{1, 2 | *lambda a, b: a+b}}", {}, '3'),
        # {{ x, y | lambda a:sum(a)}} => (lambda a: sum(a))((x, y))
    ("{{1, 2 | lambda a:sum(a)}}", {}, '3'),

        # 180
        # {{ [1,2,3] | len }} => len([1,2,3])
    ("{{ [1,2,3] | len }}", {}, '3'),
        # {{ 1 | &isinstance:int }} => (1, isinstance(1, int)) => (1, True)
    #("{{ 1 | ifelse: (lambda a: isinstance(a, int)), (lambda b: (b, True)), None }}", {}, "(1, True)"),
        # {{ x, y, z | &tuple }} => (x, y, z, tuple(x, y, z))
    ("{{ 1,2,3 | :_[0],_[1],_[2],_ }}", {}, "(1, 2, 3, (1, 2, 3))"),
        # {{ x, y, z | *&filter: w }} => (x, y, z, filter(x, y, z, w))
    ("{{(1,2), (3,4), (5,6) | *lambda a, b, c, d = (7, 8): a,b,c, dict([a,b,c,d])}}", {}, "((1, 2), (3, 4), (5, 6), {1: 2, 3: 4, 5: 6, 7: 8})"),
        # {{ x, y, z | *filter: w }} => filter(x, y, z, w)
    ("{{(1,2), (3,4), (5,6) | *lambda a, b, c, d = (7, 8): dict([a,b,c,d])}}", {}, "{1: 2, 3: 4, 5: 6, 7: 8}"),
        # {{ x, y, z | &filter: w }} => (x, y, z, filter((x, y, z), w)
    ("{{(1,2), (3,4), (5,6) | lambda a, b = (7, 8): a + (dict(list(a + (b, ))),)}}", {}, "((1, 2), (3, 4), (5, 6), {1: 2, 3: 4, 5: 6, 7: 8})"),

    ('{{"a,b,c,d", "," | repr}}', {}, "('a,b,c,d', ',')"),
    ('{{ 1, | repr }}', {}, '(1,)'),
    ('{{ 1 | :(_,) }}', {}, '(1,)'),
    #('{{x | ifelse: (lambda a: isinstance(a, int)), (lambda a: (a, a)), (lambda a: (a, None)) | :_[1] }}', {'x': None}, 'None'),
    #('{{x | ifelse: (lambda a: isinstance(a, int)), (lambda a: (a, a+1)), (lambda a: (a, 3)) | :_[1] }}', {'x': 1}, '2'),

    ("{{ x | :(_, _+'.html') | :_[0]+_[1] }}", {'x': 'test'}, 'testtest.html'),

    # abs with sign
    ("{{'-1' | @abs}}", {}, '1'),

    # split limit
    ("{{'a,b,c,d' | @split: ',', 1 | @join: '_'}}", {}, 'a_b,c,d'),
    ("{{'a,b,c,d' | @split: '', 0 | @join: '_'}}", {}, 'a,b,c,d'),
    ("{{'abcd' | @split: '', 1 | @join: '_'}}", {}, 'a_bcd'),
    ("{{ (('a', 'b')) | *lambda _1, _2: _1 + _2 }}", {}, 'ab'),
    ("{{ (('a', 'b')) | len: }}", {}, '2'),
    ("{{ (('a', 'bc')) | len: _1 }}", {}, '1'),
    ("{{ (('a', 'bc')) | len: _2 }}", {}, '2'),
    ("{{ '' | ?bool | =:'Yes' | !:'No' }}", {}, 'No'),
    ("{{ '' | ?bool | !:'No' | =:'Yes' }}", {}, 'No'),
    ("{{ '1' | ? | =:'Yes' | !:'No' }}", {}, 'Yes'),
    ("{{ '1' | ? | !:'No' | =:'Yes' }}", {}, 'Yes'),
    ('{{x | ?! :"empty" | @append: ".txt"}}', {'x': ''}, 'empty.txt'),
    ('{{x | ?! :"empty" | @append: ".txt"}}', {'x': 'a'}, 'a'),
    ('{{x | ?= :"assigned" | @append: ".txt"}}', {'x': ''}, ''),
    ('{{x | ?= :"assigned" | @append: ".txt"}}', {'x': 'a'}, 'assigned.txt'),
    ("{{x | ?.endswith('.gz') | !@append: '.gz'}}", {'x': "a"}, 'a.gz'),
    ("{{x | ?.endswith('.gz') | !@append: '.gz'}}", {'x': "a.gz"}, 'a.gz'),
    ("{{x | ?.endswith('.gz') | =:_[:-3]}}", {'x': "a"}, 'a'),
    ("{{x | ?.endswith('.gz') | =:_[:-3]}}", {'x': "a.gz"}, 'a'),
    ("{{ '' | ?bool | !:'No' | =:'Yes' }}", {}, 'No'),
    # full
    ("{{ x | ?bool | =:'Yes' | !:'No' | @append: 'Sir' }}", {'x': True}, 'Yes'),
    ("{{ x | ?bool | =:'Yes' | !:'No' | @append: 'Sir' }}", {'x': False}, 'NoSir'),
    ("{{ x | ?bool | =:'Yes' | !:'No' | $@append: 'Sir' }}", {'x': True}, 'YesSir'),
    # bool shortcut
    ("{{ x | ? | !:'No' | =:'Yes' | @append: 'Sir' }}", {'x': True}, 'YesSir'),
    ("{{ x | ? | !:'No' | =:'Yes' | @append: 'Sir' }}", {'x': False}, 'No'),
    ("{{ x | ? | !:'No' | =:'Yes' | $@append: 'Sir' }}", {'x': False}, 'NoSir'),
    # nested
    ("{{ x | ? | =:'Yes' | ? | !:'No' | @append: 'Sir' }}", {'x': True}, 'Yes'),
    ("{{ x | ? | =:'Yes' | ? | !:'No' | @append: 'Sir' }}", {'x': False}, 'False'),
    ("{{ x | ? | =:'Yes' | $? | !:'No' | @append: 'Sir' }}", {'x': True}, 'Yes'),
    ("{{ x | ? | =:'Yes' | $? | !:'No' | @append: 'Sir' }}", {'x': False}, 'NoSir'),
    ("{{ x | ? | =:'Yes' | ? | !:'No' | $@append: 'Sir' }}", {'x': True}, 'YesSir'),
    ("{{ x | ? | =:'Yes' | ? | !:'No' | $@append: 'Sir' }}", {'x': False}, 'False'),
    # combined
    ("{{ x | ?!:'No' | ?=:'Yes' | @append: 'Sir' }}", {'x': True}, 'True'),
    ("{{ x | ?=:'Yes' | ?!:'No' | @append: 'Sir' }}", {'x': False}, 'False'),
    ("{{ x | ?!:'No' | $?=:'Yes' | @append: 'Sir' }}", {'x': True}, 'YesSir'),
    ("{{ x | ?=:'Yes' | $?!:'No' | @append: 'Sir' }}", {'x': False}, 'NoSir'),
    ("{{ x | ?!:'No' | ?=:'Yes' | $@append: 'Sir' }}", {'x': True}, 'True'),
    ("{{ x | ?=:'Yes' | ?!:'No' | $@append: 'Sir' }}", {'x': False}, 'False'),
    ("{{ x | ?!:'No' | ?=:'Yes' | $@append: 'Sir' | $@append: 'Sir'}}", {'x': True}, 'TrueSir'),
    ("{{ x | ?=:'Yes' | ?!:'No' | $@append: 'Sir' | $@append: 'Sir'}}", {'x': False}, 'FalseSir'),
    # mixed
    ("{{ x | ?!:'No' | ? | =:'Yes' | @append: 'Sir' }}", {'x': True}, 'True'),
    ("{{ x | ?!:'No' | ? | =:'Yes' | $@append: 'Sir' }}", {'x': True}, 'True'),
    ("{{ x | ?!:'No' | $? | =:'Yes' | @append: 'Sir' }}", {'x': True}, 'YesSir'),
    # absence
    ("{{ x | ?.endswith: '.gz' | ! @append: '.gz' }}", {'x': 'a'}, 'a.gz'),
    ("{{ x | ?.endswith: '.gz' | ! @append: '.gz' }}", {'x': 'a.gz'}, 'a.gz'),

    ("{{ x | ?=:'Yes' | ? | !:'No' | .startswith: 'Y' }}", {'x': False}, 'False'),
    ("{{ x | ?=:'Yes' | $? | !:'No' | .startswith: 'Y' }}", {'x': False}, 'False'),
    ("{{ x | ?=:'Yes' | $? | !:'No' | $.startswith: 'Y' }}", {'x': False}, 'False'),
    ("{{ x | ? | =:'Yes' | !:'No' | .startswith: 'Y' }}", {'x': True}, 'Yes'),
    ("{{ x | ? | =:'Yes' | !:'No' | $.startswith: 'Y' }}", {'x': True}, 'True'),
    ("{{ x | ?=:'Yes' | ? | !:'No' | [0] }}", {'x': False}, 'False'),
    ("{{ x | ?=:'Yes' | $? | !:'No' | [0] }}", {'x': False}, 'N'),
    ("{{ x | ? | =:'Yes' | !:'No' | [0] }}", {'x': True}, 'Yes'),
    ("{{ x | ? | =:'Yes' | !:'No' | $[0] }}", {'x': True}, 'Y'),
    ("{{ x | ? | bool | =:'Yes' | !:'No' | $[0] }}", {'x': True}, 'Y'),
    ("{% from pathlib import Path %}{{ x | Path | ?.suffix | :_ == '.txt' | !_ | =.with_suffix: '.xlsx' }}",   {'x': '/a/b/c.py'}, '/a/b/c.py'),
    ("{% from pathlib import Path %}{{ x | Path | ?.suffix | :_ == '.txt' | !_ | =.with_suffix: '.xlsx' }}",   {'x': '/a/b/c.txt'}, '/a/b/c.xlsx'),

])
def test_render(text, data, out, debug_on):
    l = Liquid(text)
    assert l.render(**data) == out

@pytest.mark.parametrize('text, exception, exmsg', [
    ('''{% capture x %}
        wrer
        {% endcapture %}
        b
        a
        {% if %}{%endif%}''', LiquidSyntaxError, "No expressions for 'if' node"),
    ('{% for %}', LiquidSyntaxError, "'for' node expects format: 'for var1, var2 in expr'"),
    ('{% cycle 1,2,3 %}', LiquidSyntaxError, "'cycle' node must be in a 'for/while' loop"),
    ('{% while %}', LiquidSyntaxError, "No expressions for 'while' node"),
    ('{% break %}', LiquidSyntaxError, "'break' node must be in a 'for/while' loop"),
    ('{% elsif x %}', LiquidSyntaxError, "'elsif' must be in an 'if/unless/case' node"),
    ('{% else %}', LiquidSyntaxError, "'else' must be in an 'if/unless/case' node"),
    ('{% endif x %}', LiquidSyntaxError, "End node should take no expressions"),
    ('{% endif %}', LiquidSyntaxError, "Got closing node 'endif', but no node opened"),
    ('{% aendx %}', LiquidSyntaxError, "Unknown node 'aendx'"),
    ('{% continue %}', LiquidSyntaxError, "'continue' node must be in a 'for/while' loop"),
    ('{% when x %}', LiquidSyntaxError, "'when' node must be in a 'case' node"),
    ('{% endcapture %}', LiquidSyntaxError, "Got closing node 'endcapture', but no node opened"),
    ('{% if x %}{% endfor %}', LiquidSyntaxError, "Unmatched closing node 'endfor' for 'if'"),
    ('{% if x %}', LiquidSyntaxError, "Node 'if' not closed"),
    ('{{ x | @nosuch }}', LiquidSyntaxError, "Unknown liquid filter: '@nosuch'"),
    ('{%while true%}{% break 1 %}{%endwhile%}', LiquidSyntaxError, "No expressions allowed for 'break'"),
    ('{% assign %}', LiquidSyntaxError, "Malformat 'assign' node, expect 'assign a, b = 1 + `2 | @plus: 1`'"),
    ('{% increment %}', LiquidSyntaxError, "No variable specified for 'increment'"),
    ('{% decrement %}', LiquidSyntaxError, "No variable specified for 'decrement'"),
    ('{% assign x %}', LiquidSyntaxError, "Malformat 'assign' node, expect 'assign a, b = 1 + `2 | @plus: 1`'"),
    ('{% if x %}{% else x %}{% endif %}', LiquidSyntaxError, "No expressions allowed for 'else' node"),
    ('{% if x %}{% else if %}{% endif %}', LiquidSyntaxError, "No expressions for 'else if' node"),
    ('{% if x %}{% elseif %}{% endif %}', LiquidSyntaxError, "No expressions for 'elseif' node"),
    ('{% if x %}{% elsif %}{% endif %}', LiquidSyntaxError, "No expressions for 'elsif' node"),
    ('{% if x %}{% elif %}{% endif %}', LiquidSyntaxError, "No expressions for 'elif' node"),
    ('{%  %}', LiquidSyntaxError, 'Empty node'),
    ('{% raw %}', LiquidSyntaxError, "Expecting an end node for 'raw'"),
    #('{% mode  %}', LiquidSyntaxError, "Expecting a mode value"),
    ('{% block  %}', LiquidSyntaxError, "A block name is required"),
    #('{% mode aa debug cc %}', LiquidSyntaxError, "Mode can only take at most 2 values"),
    #('{% mode aa debug %}', LiquidSyntaxError, "Not a valid mode: 'aa'"),
    #('{% mode loose notaloglevel %}', LiquidSyntaxError, "Not a valid loglevel: 'NOTALOGLEVEL'"),
    ('{% comment # * // %}', LiquidSyntaxError, "Comments can only be wrapped by no more than 2 strings"),
    ('{% assign x = 1 %}{% extends x.liq %}', LiquidSyntaxError, "Cannot find file for extension: x.liq"),
    # ('{{% extends {}/templates/parent1.liq %}}{{{{  1  }}}}'.format(HERE),
    # 	LiquidSyntaxError, "Only blocks allowed in template extending others"),
    # ('{{% extends {}/templates/parent1.liq %}}{{%  assign a = 1  %}}'.format(HERE),
    # 	LiquidSyntaxError, "Only blocks allowed in template extending others"),
    ('{{ "" | *.join: }}', LiquidSyntaxError, "Attribute filter should not have modifiers"),
    ('{{ "" | @:_ }}', LiquidSyntaxError, "Liquid modifier should not go with lambda shortcut"),
    ('{{ "" | }}', LiquidSyntaxError, "No filter specified"),
    ('{{ }}', LiquidSyntaxError, "Empty node"),
    ('{{ "" | ??!bool }}', LiquidSyntaxError, 'Single ternary modifier (?/!/=) cannot be used'
                'together with ?! or ?='),
    ('{{ "" | ?!?=bool }}', LiquidSyntaxError, 'Positive/negative ternary modifier '
                '(?=/?!) cannot be used together'),
    ('{{ "" | ?*!bool }}', LiquidSyntaxError, 'Modifier (?) and (=/!) should not be '
                'used separately in one filter. Do you mean (?!/?=)?'),
    ('{{ "" | ?bool | !="Yes"}}', LiquidSyntaxError, 'Modifier (=) and (!) cannot be used together'),
    ('{{ "" | ??bool}}', LiquidSyntaxError, 'Redundant modifiers found: \'?\''),
    ('{{ "" | ? }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{{ "" | ? | !:_ | !:_ }}', LiquidSyntaxError, 'False action has already been defined'),
    ('{{ "" | ? | =:_ | =:_ }}', LiquidSyntaxError, 'True action has already been defined'),
    ('{{ "" | ? | ? }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{{ "" | ? | ?:_ }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{{ "" | ? | ?!:_ }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{{ "" | ? | ?=:_ }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{{ "" | ? | :_ }}', LiquidSyntaxError, 'Missing True/False actions for ternary filter'),
    ('{%raw x%}{%endraw%}', LiquidSyntaxError, "No expressions allowed for 'raw' node"),
    ('{%capture 12%}{%endcapture%}', LiquidSyntaxError, "Not a valid variable name '12' for 'capture' node"),
    ('{%case%}{%when 1%}{%endcase%}', LiquidSyntaxError, "No values found for 'case' node"),
    ('{%case x%}{%when%}{%endcase%}', LiquidSyntaxError, "No values found for 'when' node"),
    ('{%case 1%}{%endcase%}', LiquidSyntaxError, "No 'when' node found in 'case'"),
    ('{% increment 12%}', LiquidSyntaxError, "Invalid variable name '12' for 'increment' node"),
    ('{% from 12%}', LiquidSyntaxError, "Expect 'from ... import ...' in 'from' node"),
    ('{% unless %}{% endunless %}', LiquidSyntaxError, "No expressions found for 'unless' node"),
    ('{% include %}', LiquidSyntaxError, "No file to include"),
    ('{% include 1 %}', LiquidSyntaxError, "Cannot find file for inclusion: 1"),
    (f'{{% include {HERE}/templates %}}', LiquidSyntaxError, f"File not exists for inclusion: {HERE}/templates"),
    #('{{ "" | !:_ }}', LiquidSyntaxError, 'Ternary filter not open yet for True/False action'),
])
def test_initException(text, exception, exmsg):
    with pytest.raises(exception) as exc:
        Liquid(text)
    assert exmsg in str(exc.value)


def test_multiline_support(debug_on):
    liq = Liquid("""{% mode compact %}
{{ a | @append: ".html"
     | @append: ".txt"
     | @append: ".gz"}}
""")
    assert liq.render(a = 'test') == "test.html.txt.gz"

    liq = Liquid("""{% mode compact %}
{% if a == "test" or
      a == "text" %}
{{a}}
{% endif %}
""")
    assert liq.render(a = 'test') == "test"

    liq = Liquid("""{% mode compact %}
{# if a == "test" or
      a == "text" #}
""")
    assert liq.render(a = 'test') == ""

@pytest.mark.parametrize('text, data, exception, exmsg', [
    ('{{a}}', {}, LiquidRenderError, "name 'a' is not defined"),
    ('{% assign a.b = 1 %}', {}, LiquidRenderError, "name 'a' is not defined"),
    ('''{% capture x %}
        wrer
        x
        {% endcapture %}
        {{x}}
        c
        {# comment #}
        b
        a
{% assign a.b = 1 %}
''', {}, LiquidRenderError, "name 'a' is not defined"),
    #('{% mode info %}{% python 1/0 %}', {}, LiquidRenderError, "ZeroDivisionError: "),
# 	('''{% mode info loose %}
# {% assign a.b = 1 %}''', {'a': 1}, LiquidRenderError, "AttributeError: 'int' object has no attribute 'b'"),
    ('{{a.x}}', {'a': {'b': 1}}, LiquidRenderError, "[KeyError] 'x'"),
    ('{{a.x}}', {'a': [1,2,3]}, LiquidRenderError, "[TypeError] list indices must be integers or slices, not str"),
])
def test_renderException(text, data, exception, exmsg, debug_on):
    liquid = Liquid(text, **data, liquid_loglevel='debug')
    with pytest.raises(exception) as exc:
        liquid.render()
    assert exmsg in str(exc.value)

def test_include(debug_on):
    liquid = Liquid("""{{% mode compact %}}
    {{% assign x = x + 1 %}}
    {{% include {}/templates/include1.liq x %}}
    {{{{x}}}}
    """.format(HERE), liquid_loglevel='debug')
    assert liquid.render(x = 1) == '82'

    with pytest.raises(LiquidSyntaxError):
        # include self
        Liquid(from_file = HERE.joinpath('templates', 'include2.liq'))

    with pytest.raises(LiquidSyntaxError): # not exists
        Liquid('{% include xxx.liquid %}')

def test_extends():
    liquid = Liquid("""{{% mode compact %}}
    {{% extends {}/templates/parent1.liq %}}
    {{% block x %}}
    {{{{x * 10}}}}
    {{% endblock %}}
    """.format(HERE))
    liquid.render(x = 1) == '10'

    liquid = Liquid("""{{% mode compact %}}
    {{% extends {}/templates/parent2.liq %}}
    {{% block y %}}
    {{{{x * 10}}}}
    {{% endblock %}}
    """.format(HERE))
    liquid.render(x = 1) == '3'

    with pytest.raises(LiquidSyntaxError): # not exists
        Liquid("{% extends 'xxx' %}")

    # only blocks, ignored
    liquid = Liquid("""{{% mode compact %}}
    {{% block x %}}
    {{{{x * 10}}}}
    {{% endblock %}}
    """.format(HERE))
    liquid.render(x = 1) == '10'

def test_raw():
    liq = Liquid("""
                 {%- raw -%}                 {%
                 {%- endraw -%}""", liquid_loglevel='debug')
    assert liq.render() == '{%'

def test_no_parser_liquid_syntax_error():
    liq = Liquid(liquid_loglevel='debug')
    with pytest.raises(LiquidSyntaxError) as exc:
        raise LiquidSyntaxError('message', Diot(
            filename='file',
            lineno=10,
            parser=None,
        ))
    assert "file:10\nmessage" in str(exc.value)
