
`liquidpy` tries to support `liquid` filters, however, to support `python` filters themselves, we put `@` before the filters to mark it as `liquid` filters.
__`escapse_once`, `sort_natural`, `first` and `last` filters are abandoned.__

**Where you can use filters**

- In expression tags: `{{`, `}}` and `{{-`, `-}}`
- Anywhere else an expression applys, such as in `for/unless/while` conditions, `assign`, `case` block, etc.

# `liquid` filters

## Math filters
- `abs`: Returns the absolute value of a number.
  ```liquid
  {{ -17 | @abs }}
  {# output: 17 #}

  {{ 4 | @abs }}
  {# output: 4 #}

  {{ "-19.86" | @abs }}
  {# output: 19.86 #}
  ```
- `at_least`: Limits a number to a minimum value.
- `at_most`: Limits a number to a maximum value.
  ```liquid
  {{ 4 | @at_least: 5 }}
  {# output: 5 #}

  {{ 4 | @at_least: 3 }}
  {# output: 4 #}

  {{ 4 | @at_most: 5 }}
  {# output: 4 #}

  {{ 4 | @at_most: 3 }}
  {# output: 3 #}
  ```
- `ceil`: Rounds the input up to the nearest whole number.
  ```liquid
  {{ 1.2 | @ceil }}
  {# output: 2.0 #}

  {{ 2.0 | @ceil }}
  {# output: 2.0 #}

  {{ 183.357 | @ceil }}
  {# output: 184.0 #}

  {{ "3.5" | @ceil }}
  {# output: 4.0 #}
  ```
- `divided_by`: Divides a number by the specified number.
  ```liquid
  {{ 16 | @divided_by: 4 | int }}
  {# output: 4 #}

  {{ 5 | @divided_by: 3 | int }}
  {# output: 1 #}
  ```
- `floor`: Rounds a number down to the nearest whole number.
  ```liquid
  {{ 1.2 | @floor }}
  {# output: 1.0 #}

  {{ 2.0 | @floor }}
  {# output: 2.0 #}

  {{ 183.357 | @floor }}
  {# output: 183.0 #}

  {{ "3.5" | @floor }}
  {# output: 3.0 #}
  ```
- `minus`: Subtracts a number from another number.
  ```liquid
  {{ 4 | @minus: 2 }}
  {# output: 2 #}

  {{ 16 | @minus: 4 }}
  {# output: 12 #}

  {{ 183.357 | @minus: 12 }}
  {# output: 171.357 #}
  ```
- `modulo(mod)`: Returns the remainder of a division operation.
  ```liquid
  {{ 3 | @modulo: 2 }}
  {# python2 output: 1 #}
  {# python3 output: 1.0 #}

  {{ 24 | @mod: 7 | int }}
  {# output: 3 #}

  {{ 183.357 | @mod: 12 | int }}
  {# output: 3 #}
  ```
- `plus`: Adds a number to another number.
  ```liquid
  {{ 4 | @plus: 2 }}
  {# output: 6 #}

  {{ 16 | @plus: 4 }}
  {# output: 20 #}

  {{ 183.357 | @plus: 12 }}
  {# output: 195.357 #}
  ```
- `round`: Rounds an input number to the nearest integer or, if a number is specified as an argument, to that number of decimal places.
  ```liquid
  {{ 1.2 | @round }}
  {# output: 1 #}

  {{ 2.7 | @round }}
  {# output: 3 #}

  {{ 183.357 | @round: 2 }}
  {# output: 183.36 #}
  ```
- `times` Multiplies a number by another number.
  ```liquid
  {{ 3 | @times: 2 }}
  {# output: 6 #}

  {{ 24 | @times: 7 }}
  {# output: 168 #}

  {{ 183.357 | @times: 12 }}
  {# output: 2200.284 #}
  ```

## String filters
- `append`: Concatenates two strings and returns the concatenated value.
  ```liquid
  {{ "/my/fancy/url" | @append: ".html" }}
  {# output: /my/fancy/url.html #}

  {% assign filename = "/index.html" %}
  {{ "website.com" | @append: filename }}
  {# output: website.com/index.html #}
  ```
- `capitalize`: Makes the first character of a string capitalized.
  ```liquid
  {{ "title" | @capitalize }}
  {# output: Title #}

  {{ "my great title" | @capitalize }}
  {# output: My great title #}
  ```
- `downcase`: Makes each character in a string lowercase. It has no effect on strings which are already all lowercase.
  ```liquid
  {{ "Parker Moore" | @downcase }}
  {# output: parker moore #}

  {{ "apple" | @downcase }}
  {# output: apple #}
  ```
- `escapse`: Escapes a string by replacing characters with escape sequences (so that the string can be used in a URL, for example). It doesn’t change strings that don’t have anything to escape.
  ```liquid
  {{ "Have you read 'James & the Giant Peach'?" | @escape }}
  {# output: Have you read 'James &amp; the Giant Peach'? #}

  {{ "Tetsuro Takara" | @escape }}
  {# output: Tetsuro Takara #}
  ```
- `join`: Combines the items in an array into a single string using the argument as a separator.
  ```liquid
  {% assign beatles = "John, Paul, George, Ringo" | @split: ", " %}
  {{ beatles | join: " and " }}
  {# output: John and Paul and George and Ringo #}
  ```
- `lstrip`: Removes all whitespaces (tabs, spaces, and newlines) from the beginning of a string. The filter does not affect spaces between words.
  ```liquid
  {{ "          So much room for activities!          " | @lstrip }}
  {# output: So much room for activities!           #}
  ```
- `newline_to_br(nl2br)`: Replaces every newline (`\n`) with an HTML line break (`<br />`).
  ```liquid
  {% capture string_with_newlines %}
  Hello
  there
  {% endcapture %}
  {{ string_with_newlines | @newline_to_br }}
  {# output: Hello<br />there<br /> #}
  ```
- `prepend`: Adds the specified string to the beginning of another string.
  ```liquid
  {{ "apples, oranges, and bananas" | @prepend: "Some fruit: " }}
  {# output: Some fruit: apples, oranges, and bananas #}

  {% assign url = "liquidmarkup.com" %}
  {{ "/index.html" | @prepend: url }}
  {# output: liquidmarkup.com/index.html #}
  ```
- `remove`: Removes every occurrence of the specified substring from a string.
- `remove_first`: Removes only the first occurrence of the specified substring from a string.
  ```liquid
  {{ "I strained to see the train through the rain" | @remove: "rain" }}
  {# output: I sted to see the t through the #}

  {{ "I strained to see the train through the rain" | @remove_first: "rain" }}
  {# output: I sted to see the train through the rain #}
  ```
- `replace`: Replaces every occurrence of an argument in a string with the second argument.
- `replace_first`: Replaces only the first occurrence of the first argument in a string with the second argument.
  ```liquid
  {{ "Take my protein pills and put my helmet on" | @replace: "my", "your" }}
  {# output: Take your protein pills and put your helmet on #}

  {% assign my_string = "Take my protein pills and put my helmet on" %}
  {{ my_string | @replace_first: "my", "your" }}
  {# output: Take your protein pills and put my helmet on #}
  ```
- `rstrip`: Removes all whitespaces (tabs, spaces, and newlines) from the end of a string. The filter does not affect spaces between words.
  ```liquid
  {{ "          So much room for activities!          " | @rstrip }}
  {# output:           So much room for activities! #}
  ```
- `slice`: Returns a substring of 1 character beginning at the index specified by the argument passed in. An optional second argument specifies the length of the substring to be returned.
  ```liquid
  {{ "Liquid" | @slice: 0 }}
  {# output: L #}

  {{ "Liquid" | @slice: 2 }}
  {# output: q #}

  {{ "Liquid" | @slice: 2, 5 }}
  {# output: quid #}

  {{ "Liquid" | @slice: -3, 2 }}
  {# output: ui #}
  ```
- `split`: Divides an input string into an array using the argument as a separator.
  ```liquid
  {% assign beatles = "John, Paul, George, Ringo" | @split: ", " %}
  {% for member in beatles %}
    {{- member -}},
  {% endfor %}
  {# output: John,Paul,George,Ringo, #}
  ```
- `strip`: Removes all whitespace (tabs, spaces, and newlines) from both the left and right side of a string. It does not affect spaces between words.
  ```liquid
  {{ "          So much room for activities!          " | @strip }}
  {# output: So much room for activities! #}
  ```
- `strip_html`: Removes any HTML tags from a string.
  ```liquid
  {{ "Have <em>you</em> read <strong>Ulysses</strong>?" | @strip_html }}
  {# output: Have you read Ulysses? #}
  ```
- `strip_newlines`: Removes any newline characters (line breaks) from a string.
  ```liquid
  {% capture string_with_newlines %}
  Hello
  there
  {% endcapture %}
  {{ string_with_newlines | @strip_newlines }}
  {# output: Hellothere #}
  ```
- `truncate`: Shortens a string down to the number of characters passed as a parameter. If the number of characters specified is less than the length of the string, an ellipsis (…) is appended to the string and is included in the character count.
- `truncatewords`: Shortens a string down to the number of words passed as the argument. If the specified number of words is less than the number of words in the string, an ellipsis (…) is appended to the string.
  ```liquid
  {{ "Ground control to Major Tom." | @truncate: 20 }}
  {# output: Ground control to... #}

  {{ "Ground control to Major Tom." | @truncate: 25, ", and so on" }}
  {# output: Ground control, and so on #}

  {{ "Ground control to Major Tom." | @truncate: 20, "" }}
  {# output: Ground control to Ma #}

  {{ "Ground control to Major Tom." | @truncatewords: 3 }}
  {# output: Ground control to... #}

  {{ "Ground control to Major Tom." | @truncatewords: 3, "--" }}
  {# output: Ground control to-- #}

  {{ "Ground control to Major Tom." | @truncatewords: 3, "" }}
  {# output: Ground control to #}
  ```
- `upcase`: Makes each character in a string uppercase. It has no effect on strings which are already all uppercase.
  ```liquid
  {{ "Parker Moore" | @upcase }}
  {# output: PARKER MOORE #}

  {{ "APPLE" | @upcase }}
  {# output: APPLE #}
  ```
- `url_encode`: Converts any URL-unsafe characters in a string into percent-encoded characters using `cgi.urlencode`.
- `url_decode`: Decodes a string that has been encoded as a URL or by `cgi.unquote`.
  ```liquid
  {{ "%27Stop%21%27%20said%20Fred" | @url_decode }}
  {# output: 'Stop!' said Fred #}

  {{ "john@liquid.com" | @url_encode }}
  {# output: john%40liquid.com #}

  {{ "Tetsuro Takara" | @url_encode }}
  {# output: Tetsuro+Takara #}
  ```

## List/Array filters
- `compact`: Removes any empty values from an array.
  ```liquid
  {% assign site_categories = site.pages | @map: 'category' %}
  {% for category in site_categories %}
    {{ category }}
  {% endfor %}
  {% comment %}
  Output:
    business
    celebrities

    lifestyle
    sports

    technology
  {% endcomment %}

  {% assign site_categories = site.pages | @map: 'category' | @compact %}
  {% for category in site_categories %}
    {{ category }}
  {% endfor %}
  {% comment %}
  Output:
    business
    celebrities
    lifestyle
    sports
    technology
  {% endcomment %}
  ```
- `concat`: Concatenates (joins together) multiple arrays. The resulting array contains all the items from the input arrays.
  ```liquid
  {% assign fruits = "apples, oranges, peaches" | @split: ", " %}
  {% assign vegetables = "carrots, turnips, potatoes" | @split: ", " %}
  {% assign everything = fruits | @concat: vegetables %}
  {% for item in everything %}
  - {{ item }}
  {% endfor %}
  {% comment %}
  Output:
  - apples
  - oranges
  - peaches
  - carrots
  - turnips
  - potatoes
  {% endcomment %}
  ```
- `map`: Creates an array of values by extracting the values of a named property from another object.
  ```liquid
  {% assign all_categories = site.pages | @map: "category" %}
  {% for item in all_categories %}
  {{ item }}
  {% endfor %}
  {% comment %}
  Output:
  business
  celebrities
  lifestyle
  sports
  technology
  {% endcomment %}
  ```
- `reverse`: Reverses the order of the items in an array. reverse cannot reverse a string.
  ```liquid
  {% assign my_array = "apples, oranges, peaches, plums" | @split: ", " %}
  {{ my_array | @reverse | @join: ", " }}
  {# output: plums, peaches, oranges, apples #}
  ```
- `sort`: Sorts items in an array by a property of an item in the array. The order of the sorted array is case-sensitive.
  ```liquid
  {% assign my_array = "zebra, octopus, giraffe, Sally Snake" | @split: ", " %}
  {{ my_array | @sort | @join: ", " }}
  {# output: Sally Snake, giraffe, octopus, zebra #}
  ```
- `uniq`: Removes any duplicate elements in an array (order not preserved).
  ```liquid
  {% assign my_array = "ants, bugs, bees, bugs, ants" | split: ", " %}
  {{ my_array | @uniq | @join: ", " | @sort }}
  {# output: ants, bugs, bees #}
  ```

## Other filters
- `date`: Converts a date format into another date format. The format for this syntax is the same as `datetime.datetime.strptime` and `datetime.datetime.strftime`
  ```liquid
  {% assign article = lambda: None %}
  {% assign article.published_at = '07/17/2015' %}
  {{ article.published_at | @date: "%a, %b %d, %y", "%m/%d/%Y" }}
  {# output: Fri, Jul 17, 15 #}

  {{ article.published_at | @date: "%Y", "%m/%d/%Y" }}
  {# output: 2015 #}

  {{ "March 14, 2016" | @date: "%b %d, %y", "%B %d, %Y" }}
  {# output: Mar 14, 16 #}

  This page was last updated at {{ "now" | @date: "%Y-%m-%d %H:%M" }}.
  {# output: This page was last updated at 2018-09-19 21:18 #}
  ```
- `default`: Allows you to specify a fallback in case a value if falsy.
  ```liquid
  {% assign product_price = None %}
  {{ product_price | @default: 2.99 }}
  {# output: 2.99 #}

  {% assign product_price = 4.99 %}
  {{ product_price | @default: 2.99 }}
  {# output: 4.99 #}

  {% assign product_price = "" %}
  {{ product_price | @default: 2.99 }}
  {# output: 2.99 #}
  ```
- `size`: Equivalent of `len` in python
  ```liquid
  {{ "Ground control to Major Tom." | @size }}
  {# output: 28 #}

  {% assign my_array = "apples, oranges, peaches, plums" | @split: ", " %}
  {{ my_array | @size }}
  {# output: 4 #}
  ```

# Python filters

## Position of arguments
For all liquid filters, the argument should be at the first place. So it can be omitted. For example, `{{ 1.234 | @round: 2}}` is actually compiled as `round(1.234, 2)`. We can also specify the position of the arguments explictly:

```liquid
{{2 | @round: 1.234, _}}
{# 1.23 #}
```

If you have a tuple as your base value, you can use `_1`, `_2`, ..., `_N` for each element, respectively. For example:
```liquid
{{2, 1.234 | *@round: _2, _1}}
{# 1.23 #}
```

```liquid
{{1.234, 2 | *@round}}
{# 1.23 #}
```

See section [Modifiers](https://liquidpy.readthedocs.io/en/latest/modifiers/) for details of unpacking modifier.

## Direct filters
Any function in the environment that takes the first arguments as the values on the left of the expression (value before `|`) could be used as direct filters:
```liquid
{{"123" | len}}
{# output: 3 #}

{{ 1.234, 2 | *round }}
{# output: 1.23 #}
```

Extra arguments can be pass as `liquid` filters:
```liquid
{{ 1.234 | round: 2 }}
{# output: 1.23 #}
```

You may also define a function and then pass it to the environment of the template compilation:
```python
def someComplicatedLogic(val):
	# your logic goes here
	return val

liq = Liquid('{{ "value" | myfilter }}', {'myfilter': someComplicatedLogic})
liq.render()
```

## Getitem filters
You can get the items directly from the values on the left:
```liquid
{{ [1,2,3] | [0] }}
{# output: 1 #}

{{ [1,2,3] | [1:] | sum }}
{# output: 5 #}

{{ {"a": 1} | ["a"] }}
{# output: 1 #}

{{ {"a": {"b": (lambda x: x*10)} } | ["a"].b: 10 }}
{# output: 100 #}
```

Remember if you if have multiple values on the left, they will be treated as a `tuple`:
```liquid
{{ 1.234, 2 | [1] }}
{# output: 2 #}
```

## Attribute filters
Get the value from the attribute of an object. If it is `callable`, you can also use it as a filter:
```liquid
{{ "," | .join: ['a', 'b'] }}
{# output: a,b #}

{{ "{}, {}!" | .format: "Hello", "world" }}
{# output: Hello, world! #}

{{ {"x": "{}, {}!"} | .x.format: "Hello", "world" }}
{# output: Hello, world! #}
```

Get non-callable attribute values:
```liquid
{{ '' | .__doc__ }}
{# output: str(object='') ... #}
```

What if callable attribute takes no argument:
```liquid
{{ '1' | .isdigit }}
{# output: <function isdigit> #}
```

To call it:
```liquid
{{ '1' | .isdigit() }}
{# or #}
{{ '1' | .isdigit: }}
```

## Lambda filters
You may also apply lambda filters:
```liquid
{% import os %}
{{ "/path/to/file.txt" | lambda p: os.path.join(
                            os.path.dirname(p),
                            os.path.splitext(p)[0]
                          + '.sorted'
                          + os.path.splitext(p)[1] ) }}
{# output: /path/to/file.sorted.txt #}
```

With a single element as base value, you can even omit the `lambda` keyword and `_` will be used as the argument:
```
{% import os %}
{{ "/path/to/file.txt" | : os.path.join(os.path.dirname(_),
                                        os.path.splitext(_)[0]
                                      + '.sorted'
                                      + os.path.splitext(_)[1] ) }}
{# output: /path/to/file.sorted.txt #}
```

## ternary filters
- Full format

  ```liquid
  {{ x | ?isinstance: list
       | =: "A list with length %s" % len(_)
       | !: "Other iterable with length %s" % len(_) }}

  {# liquid.render(x = [1,2,3]): A list with length 3 #}
  {# liquid.render(x = "123"): Other iterable with length 3 #}
  ```

  You can also switch the position of True/False actions:
  ```liquid
  {{ x | ?isinstance: list
       | !: "Other iterable with length %s" % len(_)
       | =: "A list with length %s" % len(_) }}
  ```

- Bool shortcut

  ```liquid
  {{ x | ? | =:'Yes' | !:'No' | @append: ', Sir!' }}
  {# is equivalent to #}
  {{ x | ?bool | =:'Yes' | !:'No' | @append: ', Sir!' }}

  {# liquid.render(x = True): Yes, Sir! #}
  {# liquid.render(x = 1): Yes, Sir! #}
  {# liquid.render(x = []): No, Sir! #}
  {# liquid.render(x = 0): No, Sir! #}
  {# liquid.render(x = ''): No, Sir! #}
  ```

- Absence of either action

  ```liquid
  {{ x | ?.endswith: '.gz' | !@append: '.gz' }}

  {# liquid.render(x = 'a'): a.gz #}
  {# liquid.render(x = 'a.gz'): a.gz #}
  ```
  ```liquid
  {{ x | ?.endswith: '.gz' | = :_[:-3] }}

  {# liquid.render(x = 'a'): a #}
  {# liquid.render(x = 'a.gz'): a #}
  ```

- Combined ternary filters `?!` and `?=`

  ```liquid
  {{ x | ?! :"empty" | @append: ".txt" }}

  {# liquid.render(x = 'a'): a.txt #}
  {# liquid.render(x = ''): empty.txt #}
  ```

  ```liquid
  {{ x | ?= @append: ".txt" | @prepend: "[" @append: "]"}}

  {# liquid.render(x = 'a'): [a.txt] #}
  {# liquid.render(x = ''):  [] #}
  ```

- Mixed use

  ```liquid
  {{ x | ?!:'No' | ? | =:'Yes' | @append: ', Sir' }}

  {# liquid.render(x = True):  Yes, Sir! #}
  {# liquid.render(x = False): No, Sir! #}
  ```




