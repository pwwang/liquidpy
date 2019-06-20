import sys
from os import path
import pytest
import liquid
from box import Box
from liquid import Liquid, LiquidSyntaxError, LiquidRenderError

Liquid.DEBUG = False
Liquid.MODE  = 'mixed'

@pytest.mark.parametrize('text, data, out', [
	('{{ page.title }}', {'page': Box(title = 'Introduction')}, 'Introduction'),
	('''{% if user %}
Hello {{ user.name }}!{% endif %}''', {'user': Box(name = 'Adam')}, 'Hello Adam!'),
	('''{% if product.title == "Awesome Shoes" %}
  These shoes are awesome!{% endif %}''', {'product': Box(title = 'Awesome Shoes')}, '  These shoes are awesome!'),
	('''{% if product.type == "Shirt" or product.type == "Shoes" %}
  This is a shirt or a pair of shoes.{% endif %}''', {'product': Box(type = 'Shirt')}, '''  This is a shirt or a pair of shoes.'''),
		# python 'in' used instead of liquid 'contains'
	('''{% if 'Pack' in product.title %}
  This product's title contains the word Pack.{% endif %}''', {'product': Box(title = 'whateverPack')}, '  This product\'s title contains the word Pack.'),
	('''{% if 'Hello' in product.tags %}
  This product has been tagged with 'Hello'.{% endif %}''', {'product': Box(tags = '23Hello234')}, "  This product has been tagged with 'Hello'."),

	('''{% assign tobi = "Tobi" %}

{% if tobi %}
  This condition will always be true.
{% endif %}''', {}, '''
  This condition will always be true.
'''),

		# different truthy from liquid
		# see: https://shopify.github.io/liquid/basics/truthy-and-falsy/
	('''{% if settings.fp_heading %}
  <h1>{{ settings.fp_heading }}</h1>{% endif %}''', {'settings': Box(fp_heading = 1)}, '  <h1>1</h1>'),
])
def test_render_0(text, data, out):
	l = Liquid(text)
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
	('''{% mode loose %}
{% assign my_variable = "tomato" %}
{{ my_variable }}''', {}, '''
tomato'''),
	('''{% mode loose %}
{%- assign my_variable = "tomato" -%}
{{ my_variable }}''', {}, 'tomato'),
	('''{% assign username = "John G. Chalmers-Smith" %}
{% if username and len(username) > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}
''', {}, '  Wow, John G. Chalmers-Smith, you have a long name!\n'),
	('''{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and len(username) > 10 -%}
  Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif -%}
''', {}, '  Wow, John G. Chalmers-Smith, you have a long name!\n'),

		# comments
	('''Anything you put between {% comment %} and {% endcomment %} tags
is turned into a comment.''', {}, '''Anything you put between# andtags
is turned into a comment.'''),
	('''Anything you put between {# and #} tags
is turned into a comment.''', {}, '''Anything you put betweentags
is turned into a comment.'''),
])
def test_render_1(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
		#20
		# unless
	('''{% unless product.title == 'Awesome Shoes' %}
  These shoes are not awesome.
{% endunless %}''', {'product': Box(title = 'Notawesome Shoes')}, '''  These shoes are not awesome.
'''),
		# elsif
	('''{% if customer.name == 'kevin' %}
  Hey Kevin!
{% elsif customer.name == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': Box(name = 'anonymous')}, '''  Hey Anonymous!
'''),
	('''{% if customer.name == 'kevin' %}
  Hey Kevin!
{% elseif customer.name == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': Box(name = 'anonymous')}, '''  Hey Anonymous!
'''),
	('''{% if customer.name == 'kevin' %}
  Hey Kevin!
{% else if customer.name == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}''', {'customer': Box(name = 'anonymous')}, '''  Hey Anonymous!
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
{% endcase %}''', {}, '''     This is a cake
'''),

	('''{% for product in collection.products %}
{{ product.title }}
{% endfor %}''', {'collection': Box(
	products = [
		Box(title = 'hat'),
		Box(title = 'shirt'),
		Box(title = 'pants')
	])}, '''hat
shirt
pants
'''),

	('''{% for i in range(1, 6) %}
  {% if i == 4 %}
    {% break %}
  {% else %}
    {{ i }}
  {% endif %}
{% endfor %}''', {}, '''    1
    2
    3
'''),

	('''{% for i in range(1, 6) %}
  {% if i == 4 %}
    {% continue %}
  {% else %}
    {{ i }}
  {% endif %}
{% endfor %}''', {}, '''    1
    2
    3
    5
'''),
])
def test_render_2(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
	('''{% raw %}
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
{% endraw %}''', {}, '''  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
'''),
		# assign
	('''{% assign my_variable = false %}
{% if my_variable != true %}
  This statement is valid.
{% endif %}''', {}, '  This statement is valid.\n'),
	('''{% assign foo = "bar" %}
{{ foo }}''', {}, '''bar'''),

		# capture
	('''{% capture my_variable %}I am being captured.{% endcapture %}
{{ my_variable }}''', {}, 'I am being captured.'),

		# capture
	('''{% assign favorite_food = 'pizza' %}
{% assign age = 35 %}

{% capture about_me %}
I am {{ age }} and my favorite food is {{ favorite_food }}.
{% endcapture %}

{{ about_me }}''', {}, '\n\nI am 35 and my favorite food is pizza.\n'),

		# in/decrement
	('''{% increment my_counter %}
		{{ my_counter }}
		{% increment my_counter %}
		{{ my_counter }}
		{% increment my_counter %}
		{{ my_counter }}''', {'my_counter': 0}, '''		1
		2
		3''' ),

	('''{% decrement my_counter %}
		{{ my_counter }}
		{% decrement my_counter %}
		{{ my_counter }}
		{% decrement my_counter %}
		{{ my_counter }}''', {'my_counter': 0}, '''		-1
		-2
		-3''' ),

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
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
	('''{% assign site_categories = site.pages | @map: 'category' %}

{% for category in site_categories %}
  {{ category }}
{% endfor %}''', {'site': Box(pages = [
	Box(category = 'business'),
	Box(category = 'celebrities'),
	Box(category = ''),
	Box(category = 'lifestyle'),
	Box(category = 'sports'),
	Box(category = ''),
	Box(category = 'technology')
])}, '''
  business
  celebrities\n  \n  lifestyle
  sports\n  \n  technology
'''),
	('''{% assign site_categories = site.pages | @map: 'category' | @compact %}

{% for category in site_categories %}
  {{ category }}
{% endfor %}''', {'site': Box(pages = [
	Box(category = 'business'),
	Box(category = 'celebrities'),
	Box(category = ''),
	Box(category = 'lifestyle'),
	Box(category = 'sports'),
	Box(category = ''),
	Box(category = 'technology')
])}, '''
  business
  celebrities
  lifestyle
  sports
  technology
'''),
	('''{% assign fruits = "apples, oranges, peaches" | @split: ", " %}
{% assign vegetables = "carrots, turnips, potatoes" | @split: ", " %}

{% assign everything = fruits | @concat: vegetables %}
{% for item in everything %}
- {{ item }}
{% endfor %}''', {}, '''
- apples
- oranges
- peaches
- carrots
- turnips
- potatoes
'''),
	('''{% assign furniture = "chairs, tables, shelves" | @split: ", " %}

{% assign everything = fruits | @concat: vegetables | @concat: furniture %}
{% for item in everything %}
- {{ item }}
{% endfor %}''', {'fruits': "apples, oranges, peaches".split(", "), 'vegetables': "carrots, turnips, potatoes".split(', ')}, '''
- apples
- oranges
- peaches
- carrots
- turnips
- potatoes
- chairs
- tables
- shelves
'''),
])
def test_render_4(text, data, out):
	l = Liquid(text)
	print(repr(l.render(**data)))
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
	('{{ article.published_at | @date: "%a, %b %d, %y", "%m/%d/%Y" }}', {'article': Box(published_at = '07/17/2015')}, 'Fri, Jul 17, 15'),
	('{{ article.published_at | @date: "%Y", "%m/%d/%Y" }}', {'article': Box(published_at = '07/17/2015')}, '2015'),
	('{{ "March 14, 2016" | @date: "%b %d, %y", "%B %d, %Y" }}', {}, 'Mar 14, 16'),
	('This page was last updated at {{ "now" | @date: "%Y-%m-%d %H:%M" }}.', {}, 'This page was last updated at {}.'.format(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M"))),
	('This page was last updated at {{ "today" | @date: "%Y-%m-%d %H:%M" }}.', {}, 'This page was last updated at {}.'.format(__import__('datetime').datetime.today().strftime("%Y-%m-%d %H:%M"))),

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

	('''{% assign beatles = "John, Paul, George, Ringo" | @split: ", " %}

{{ beatles | @join: " and " }}''', {}, '''
John and Paul and George and Ringo'''),

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
	('''
{% capture string_with_newlines %}
Hello
there
{% endcapture %}
{{ string_with_newlines | @newline_to_br }}''', {}, '''
Hello<br />there<br />'''),

	('{{ "apples, oranges, and bananas" | @prepend: "Some fruit: " }}', {}, 'Some fruit: apples, oranges, and bananas'),
	('''{% assign url = "liquidmarkup.com" %}

{{ "/index.html" | @prepend: url }}''', {}, '''
liquidmarkup.com/index.html'''),

	('{{ "I strained to see the train through the rain" | @remove: "rain" }}', {}, 'I sted to see the t through the '),
		# 85
	('{{ "I strained to see the train through the rain" | @remove_first: "rain" }}', {}, 'I sted to see the train through the rain'),

	('{{ "Take my protein pills and put my helmet on" | @replace: "my", "your" }}', {}, 'Take your protein pills and put your helmet on'),
	('{{ "Take my protein pills and put my helmet on" | @replace_first: "my", "your" }}', {}, 'Take your protein pills and put my helmet on'),

	('''
{% assign my_array = "apples, oranges, peaches, plums" | @split: ", " %}

{{ my_array | @reverse | @join: ", " }}''', {}, '''

plums, peaches, oranges, apples'''),

	('{{ "Ground control to Major Tom." | @split: "" | @reverse | @join: "" }}', {}, '.moT rojaM ot lortnoc dnuorG'),

	('{{ 1.2 | @round }}', {}, '1.0'),
	('{{ 2.7 | @round }}', {}, '3.0'),
		#92
	('{{ 183.357 | @round: 2 }}', {}, '183.36'),

	('{{ "          So much room for activities!          " | @rstrip }}', {}, '          So much room for activities!'),
	('{{ "          So much room for activities!          " | @strip }}', {}, 'So much room for activities!'),

	('{{ "Ground control to Major Tom." | @size }}', {}, '28'),
	('{% assign my_array = "apples, oranges, peaches, plums" | @split: ", " %}{{ my_array | @size }}', {}, '4'),

	('{{ "Liquid" | @slice: 0 }}', {}, 'L'),
	('{{ "Liquid" | @slice: 2 }}', {}, 'q'),
		# 99
	('{{ "Liquid" | @slice: 2, 5 }}', {}, 'quid'),
	('{{ "Liquid" | @slice: -3, 2 }}', {}, 'ui'),

	('{% assign my_array = "zebra, octopus, giraffe, Sally Snake" | @split: ", " %}{{ my_array | @sort | @join: ", " }}', {}, 'Sally Snake, giraffe, octopus, zebra'),
])
def test_render_6(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
	('''{% assign beatles = "John, Paul, George, Ringo" | @split: ", " %}

{% for member in beatles %}
  {{ member }}
{% endfor %}''', {}, '''
  John
  Paul
  George
  Ringo
'''),
	('{{ "Have <em>you</em> read <strong>Ulysses</strong>?" | @strip_html }}', {}, 'Have you read Ulysses?'),
		#104
	('''{% capture string_with_newlines %}
Hello
there
{% endcapture %}
{{ string_with_newlines | @strip_newlines }}''', {}, 'Hellothere',),

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

	('''{% assign my_array = "ants, bugs, bees, bugs, ants" | @split: ", " %}
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
{% endwhile %}''', {'a':0}, '''1
2
3
'''),
		# python
	('''{% python from os import path %}
{{path.basename('a/b/c')}}''', {}, 'c'),
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
{% endraw %}''', {}, '''whatever
I{% if %}
enter{% comment %}
here{% raw %}
is preversed
'''),
	('''{% comment %}
whatever
I{% if %}
enter{% comment %}
here{% raw %}
is treated as comments
{% endcomment %}''', {}, '''# whatever
# I{% if %}
# enter{% comment %}
# here{% raw %}
# is treated as comments
'''),
	('''{% capture a %}
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
	('{{ "/path/to/file.txt" | :len(a) - 4 }}', {}, '13'),
])
def test_render_8(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
	('{{ "{}, {}!" | .format: "Hello", "world" }}', {}, 'Hello, world!'),
	('''{% mode compact %}
{% python from os import path %}
{{ "/path/to/file.txt" | lambda p, path = path: path.join( path.dirname(p), path.splitext(p)[0] + '.sorted' + path.splitext(p)[1] ) }}''', {}, '/path/to/file.sorted.txt'),
	("{{ '1' | .isdigit() }}", {}, 'True'),
		# 137
	("{{ '1' | .isdigit: }}", {}, 'True'),
	("{{ x | ['a']: 1, 2 }}", {'x': {'a': lambda x, y: x+y}}, '3'),
	("{{ x | ['a'] }}", {'x': {'a': 1}}, '1'),
		# 140
	("{{ x | ['a']: }}", {'x': {'a': lambda: 2}}, '2'),
	("{{ x | ['a']() }}", {'x': {'a': lambda: 2}}, '2'),
	('''{% comment # %}
a
b
c
{% endcomment %}''', {}, '''# a
# b
# c
'''),
	('''{% comment // %}
a
b
c
{% endcomment %}''', {}, '''// a
// b
// c
'''),
		# 144
	("{{ x | &isinstance: list | [0] | sum }}", {'x': [1,2,3]}, '6'),
	("{{ x | &@append: '.html' | len }}", {'x': 'test'}, '2'),
	("{{ x | &@append: '.html' | *:a+b }}", {'x': 'test'}, 'testtest.html'),

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
	("{{ 1,2 | :a + (3,4) | sum}}", {}, '10'),
		# {{ x, y | *&@filter: a }} => (x, y, filter(x, y, a))
	("{{ 'a,b,c,d', ',' | *&@replace: '|' | :'-'.join(a) }}", {}, 'a,b,c,d-,-a|b|c|d'),
		# {{ x, y | &@filter: a }} => (x, y, filter((x, y), a))
	("{{ 1,2 | &@concat: (3,4) }}", {}, '(1, 2, (1, 2, 3, 4))'),
])
def test_render_9(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
		# 154
		# {{ x | .__file__}} => x.__file__
	("{{path | .__file__}}", {'path': path}, path.__file__),
		# {{ x | .join(["a", "b"]) }} => x.join(["a", "b"])
	("{{',' | .join(['a', 'b']) }}", {}, 'a,b'),
		# {{ x | .join: ["a", "b"]}} => x.join(["a", "b"])
	("{{',' | .join: ['a', 'b'] }}", {}, 'a,b'),
		# {{ x | &.attr }} => (x, x.attr)
	("{{'a' | &.isupper()}}", {}, "('a', False)"),
		# {{ x, y | .count(1) }} => (x, y).count(1)
	("{{ 1,2 | .count(1) }}", {}, '1'),
		# {{ x, y | .count: 1 }} => (x, y).count(1)
	("{{ 1,2 | .count: 2 }}", {}, '1'),

		# 160
		# {{ x, y | *.join: ["a", "b"] }} => x.join(["a", "b"]) # y lost!!
	("{{ ',', '.' | *.join: ['a', 'b']}}", {}, 'a,b'),
		# {{ x, y | &.count:1 }} => (x, y, (x, y).count(1))
	("{{ 1,2 | &.count: 2 }}", {}, '(1, 2, 1)'),
		# {{ x, y | *&.join: ["a", "b"] }} => (x, y, x.join(["a", "b"]))
	("{{ ',', '.' | *&.join: ['a', 'b']}}", {}, "(',', '.', 'a,b')"),

		# 163
		# {{ x | [0] }} => x[0]
	("{{[1,2] | [0]}}", {}, '1'),
		# {{ x | &[0] }} => (x, x[0])
	("{{[1,2] | &[0]}}", {}, '([1, 2], 1)'),
		# {{ x | [0](1) }} => x[0](1)
	("{{[lambda a: a*10,2] | [0](1) }}", {}, '10'),
		# {{ x | [0]: 1 }} => x[0](1)
	("{{[lambda a: a*10,2] | [0]: 1 }}", {}, '10'),
		# {{ x, y | [0] }} => (x, y)[0] == x
	("{{ [1,2], 3 | [0] }}", {}, '[1, 2]'),
		# {{ x, y | *[0] }} => x[0]
	("{{ [1,2], 3 | *[0] }}", {}, '1'),
		# {{ x, y | &[0] }} => (x, y, (x, y)[0]) == (x, y, x)
	("{{ [1,2], 3 | &[0] }}", {}, '([1, 2], 3, [1, 2])'),

		# 170
		# {{ x, y | *&[0] }} => (x, y, x[0])
	("{{ [1,2], 3 | *&[0] }}", {}, '([1, 2], 3, 1)'),
		# {{ x, y | [0]: 1 }} => (x, y)[0](1)
	("{{lambda a: a*10, 2 | [0]: 1 }}", {}, '10'),

		# 172
		# {{ x | :a[1]}} => (lambda a: a[1])(x)
	("{{[1,2] | :a[1]}}", {}, '2'),
		# {{ x | &:a[1] }} => (x, (lambda a: a[1])(x))
	("{{[1,2] | &:a[1]}}", {}, '([1, 2], 2)'),
		# {{ x, y | *:a+b }} => (lambda a, b: a+b)(x, y)
	("{{1, 2 | *:a+b}}", {}, '3'),
		# {{ x, y | :sum(a)}} => (lambda a: sum(a))((x, y))
	("{{1, 2 | :sum(a)}}", {}, '3'),
])
def test_render_10(text, data, out):
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, data, out', [
		# 176 real lambda
		# {{ x | lambda a:a[1]}} => (lambda a: a[1])(x)
	("{{ 1 | lambda a: a*10}}", {}, '10'),
		# {{ x | &lambda a:a[1] }} => (x, (lambda a: a[1])(x))
	("{{ 1 | &lambda a: a*10}}", {}, '(1, 10)'),
		# {{ x, y | *lambda a, b: a+b }} => (lambda a, b: a+b)(x, y)
	("{{1, 2 | *lambda a, b: a+b}}", {}, '3'),
		# {{ x, y | lambda a:sum(a)}} => (lambda a: sum(a))((x, y))
	("{{1, 2 | lambda a:sum(a)}}", {}, '3'),

		# 180
		# {{ [1,2,3] | len }} => len([1,2,3])
	("{{ [1,2,3] | len }}", {}, '3'),
		# {{ 1 | &isinstance:int }} => (1, isinstance(1, int)) => (1, True)
	("{{ 1 | &isinstance:int }}", {}, "(1, True)"),
		# {{ x, y, z | &tuple }} => (x, y, z, tuple(x, y, z))
	("{{ 1,2,3 | &tuple }}", {}, "(1, 2, 3, (1, 2, 3))"),
		# {{ x, y, z | *&filter: w }} => (x, y, z, filter(x, y, z, w))
	("{{(1,2), (3,4), (5,6) | *&lambda a, b, c, d = (7, 8): dict([a,b,c,d])}}", {}, "((1, 2), (3, 4), (5, 6), {1: 2, 3: 4, 5: 6, 7: 8})"),
		# {{ x, y, z | *filter: w }} => filter(x, y, z, w)
	("{{(1,2), (3,4), (5,6) | *lambda a, b, c, d = (7, 8): dict([a,b,c,d])}}", {}, "{1: 2, 3: 4, 5: 6, 7: 8}"),
		# {{ x, y, z | &filter: w }} => (x, y, z, filter((x, y, z), w)
	("{{(1,2), (3,4), (5,6) | &lambda a, b = (7, 8): dict(list(a + (b, )))}}", {}, "((1, 2), (3, 4), (5, 6), {1: 2, 3: 4, 5: 6, 7: 8})"),

	('{{"a,b,c,d", "," | repr}}', {}, "('a,b,c,d', ',')"),
	('{{ 1, | repr }}', {}, '(1,)'),
	('{{ 1 | :(a,) }}', {}, '(1,)'),
	('{{x | &isinstance: int | *:[a, b+1][int(b)] }}', {'x': None}, 'None'),
	('{{x | &isinstance: int | *:[a, b+1][int(b)] }}', {'x': 1}, '2'),

	("{{ x | :(a, a+'.html') | :a[0]+a[1] }}", {'x': 'test'}, 'testtest.html'),

	# abs with sign
	("{{'-1' | @abs}}", {}, '1'),

	# split limit
	("{{'a,b,c,d' | @split: ',', 1 | @join: '_'}}", {}, 'a_b,c,d'),
	("{{'a,b,c,d' | @split: '', 0 | @join: '_'}}", {}, 'a,b,c,d'),
	("{{'abcd' | @split: '', 1 | @join: '_'}}", {}, 'a_bcd'),
])
def test_render(text, data, out):
	Liquid.DEBUG = True
	l = Liquid(text)
	assert l.render(**data) == out

@pytest.mark.parametrize('text, exception, exmsg', [
	('''{% capture x %}
		wrer
		{% endcapture %}
		b
		a
		{% if %}{%endif%}''', LiquidSyntaxError, 'No statements for "if" at line 6: 		{% if %}'),
	('{% for %}', LiquidSyntaxError, 'No statements for "for" at line 1: {% for %}'),
	('{% while %}', LiquidSyntaxError, 'No statements for "while" at line 1: {% while %}'),
	('{% break %}', LiquidSyntaxError, '"break" must be in a loop block at line 1: {% break %}'),
	('{% elsif x %}', LiquidSyntaxError, '"elif" must be in an if/unless block at line 1: {% elsif x %}'),
	('{% else %}', LiquidSyntaxError, '"else" must be in an if/unless/case block at line 1: {% else %}'),
	('{% endif x %}', LiquidSyntaxError, 'Additional statements for endif at line 1: {% endif x %}'),
	('{% endx %}', LiquidSyntaxError, 'Unknown end tag endx at line 1: {% endx %}'),
	('{% continue %}', LiquidSyntaxError, '"continue" must be in a loop block at line 1: {% continue %}'),
	('{% when x %}', LiquidSyntaxError, 'No case opened for "when" at line 1: {% when x %}'),
	('{% endcapture %}', LiquidSyntaxError, 'Unmatched tag: /endcapture at line 1: {% endcapture %}'),
	('{% if x %}{% endfor %}', LiquidSyntaxError, 'Unmatched tag: if/endfor at line 1: {% endfor %}'),
	('{% if x %}', LiquidSyntaxError, 'Unclosed template tag: if'),
	('{{ x | @nosuch }}', LiquidSyntaxError, 'Unknown liquid filter: @nosuch at line 1: {{ x | @nosuch }}'),
	('{% break 1 %}', LiquidSyntaxError, 'Additional statements for "break" at line 1: {% break 1 %}'),
	('{% assign %}', LiquidSyntaxError, 'No statements for "assign" at line 1: {% assign %}'),
	('{% increment %}', LiquidSyntaxError, 'No variable for increment at line 1: {% increment %}'),
	('{% assign x %}', LiquidSyntaxError, 'Malformat assignment, no equal sign found: assign at line 1: {% assign x %}'),
	('{% if x %}{% else x %}{% endif %}', LiquidSyntaxError, '"Else" must be followed by "if" statement if any at line 1: {% else x %}'),
	('{% if x %}{% else if %}{% endif %}', LiquidSyntaxError, 'No statements for "else if" at line 1: {% else if %}'),
])
def test_initException(text, exception, exmsg):
	with pytest.raises(exception) as exc:
		Liquid(text)
	assert exmsg in str(exc.value)

@pytest.mark.parametrize('text, data, exception, exmsg', [
	('{{a}}', {}, LiquidRenderError, "NameError: name 'a' is not defined, in compiled source: _liquid_ret_append((a))"),
	('{% assign a.b = 1 %}', {}, LiquidRenderError, "NameError: name 'a' is not defined, at line 1: {% assign a.b = 1 %}"),
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
''', {}, LiquidRenderError, "NameError: name 'a' is not defined, at line 10: {% assign a.b = 1 %}"),
	('{% python 1/0 %}', {}, LiquidRenderError, "ZeroDivisionError: "),
	('''{% mode nodebug %}
{% assign a.b = 1 %}''', {'a': 1}, LiquidRenderError, "AttributeError: 'int' object has no attribute 'b', at line 1: {% assign a.b = 1 %}"),
])
def test_renderException(text, data, exception, exmsg):
	liquid = Liquid(text, **data)
	with pytest.raises(exception) as exc:
		liquid.render()
	assert exmsg in str(exc.value)
