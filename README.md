# liquidpy
A port of [liquid][1] template engine for python  

![Pypi][2] ![Github][3] ![PythonVers][4] ![Travis building][5]  ![Codacy][6] ![Codacy coverage][7]

## Table of Contents

   * [Install](#install)
   * [Baisic usage](#baisic-usage)
   * [Documentation](#documentation)
      * [Tags](#tags)
      * [Operators, types, truthy and falsy](#operators-types-truthy-and-falsy)
      * [White space control](#white-space-control)
      * [Blocks](#blocks)
         * [Comment](#comment)
         * [Python source](#python-source)
         * [Control flow](#control-flow)
            * [if](#if)
            * [unless](#unless)
            * [elsif(elif, else if) / else](#elsifelif-else-if--else)
            * [case/when](#casewhen)
         * [Iteration/Loop](#iterationloop)
            * [while](#while)
            * [for](#for)
            * [break/continue](#breakcontinue)
         * [Raw](#raw)
         * [Variable](#variable)
            * [assign](#assign)
            * [capture](#capture)
            * [increment](#increment)
            * [decrement](#decrement)
      * [Filters](#filters)
         * [liquid filters](#liquid-filters)
            * [Math filters](#math-filters)
            * [String filters](#string-filters)
            * [List/Array filters](#listarray-filters)
            * [Other filters](#other-filters)
         * [Python filters](#python-filters)
            * [Direct filters](#direct-filters)
            * [Getitem filters](#getitem-filters)
            * [Attribute filters](#attribute-filters)
            * [Lambda filters](#lambda-filters)

# Install
```shell
# install released version
pip install liquidpy
# install lastest version
pip install https://github.com/pwwang/liquidpy.git
```

# Baisic usage
```python
from liquid import Liquid
liq = Liquid('{{a}}')
ret = liq.render({'a': 1})
# ret == '1'
```
With environments:
```python
liq = Liquid('{{os.path.basename(a)}}', {'os': __import__('os')})
ret = liq.render({'a': "path/to/file.txt"})
# ret == 'file.txt'
```

# Documentation
`liquidpy` basically implements almost all the features supported by liquid, however, it has some differences and specific features due to the language feature itself.   
__Anything that is different from `liquid` will be underscored.__
## Tags
`liquidpy` supports all tags that `liquid` does: `{{`, `}}`, `{%`, `%}`, and their non-whitespace variants: `{{-`, `-}}`, `{%-` and `-%}`. __Beside these tags, `liquidpy` supports `{#`, `#}` (non-whitespace variants: `{#-`, `-#}` have some comments in the template.__

## Operators, types, truthy and falsy
They basically follow `python` syntax. Besides that, `liquidpy` also has `true`, `false` and `nil` keywords as `liquid` does, which correspond to `True`, `False` and `None` in `python`.  

## White space control
Same as liquid does, you can include a hyphen in your tag syntax `{{-`, `-}}`, `{%-`, `-%}`, `{#-` and `-#}` to strip whitespace from the left or right side of a rendered tag.  
They basically strip the whitespace before and after the tag, as well as the newline character in the line of the tag.  
So they match the regular expression `r'[ \t]*{{-.*?-}}[ \t]*\n?'`  
**Input**
```liquid
{% assign my_variable = "tomato" %}
{{ my_variable }}
```
**Output**
```

tomato
```
**Input**
```liquid
{%- assign my_variable = "tomato" -%}
{{ my_variable }}
```
**Output**
```
tomato
```
**Input**
```liquid
{% assign username = "John G. Chalmers-Smith" %}
{% if username and username.size > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}
```
**Output**
```


  Wow, John G. Chalmers-Smith, you have a long name!

```
**Input**
```liquid
{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and username.size > 10 -%}
  Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif -%}
```
**Output**
```
  Wow, John G. Chalmers-Smith, you have a long name!
```  

__NOTE: the leading spaces of the line is not stripped, this is slightly different from `liquid`__

__The above behavior of the tags are in `loose` mode, which is a default mode of `liquidpy`. You may also change the default mode globally:__
```python
from liquid import Liquid
Liquid.DEFAULT_MODE = 'compact'
```
__By change the default mode to `compact`, then the whitespace tags will act exactly the same as the non-whitespace tags.__  

__We also have a `mixed` mode, where only `{#` and `{%` act like `{#-` and `{%-`, as well as their closing tags. `{{` remains the same.__

__You may also change the mode for each `Liquid` instance. Put `{% mode compact %}`, `{% mode mixed %}` or `{% mode loose %}` at the _FIRST LINE_ to tell the engine to use the corresponding mode.__  
**Input**
```liquid
{% mode compact %}
{% assign username = "John G. Chalmers-Smith" %}
{% if username and username.size > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}
```
**Output**
```
  Wow, John G. Chalmers-Smith, you have a long name!
```  
___Unless decleared explictly, the mode will be `mixed` in this document.___

## Blocks
### Comment
__Unlike `liquid`, `liquidpy` has two comment systems: comment block `{% comment %}...{% endcomment %}` and comment tag `{# ... #}`.__  
__The former one is also supported by `liquid`, but acts differently. In `liquid`, anything between the comment block will be igored, however, it turns to python comments in `liquidpy`. If you want the comments to be ignore, you should use comment tag instead:__  
**Input**
```liquid
Anything you put between
{% comment %}
and 
{% endcomment %}
tags is turned into a comment.
```
**Output**
```
Anything you put between
# and
tags is turned into a comment.
```

**Input**
```liquid
Anything you put between
{# and #}
tags is turned into a comment.
```
**Output**
```
Anything you put between
tags is turned into a comment.
```

Use a different comment sign:  
**Input**
```liquid
{% comment // %}
This
will be
translated
as comments
{% endcomment %}
```
**Output**
```
// This
// will be
// translated
// as comments
```

### Python source
__You may also insert python source code to the template, one line each time__  

**Input**
```liquid
{% python from os import path %}
{% python from glob import glob %}
{% python d = './date' %}
{% for filepath in glob(path.join(d, '*.txt')) %}
  {{path.basename(filepath)}}
{% endfor %}

```
**Output**
```
  a.txt
  b.txt
```

### Control flow
#### `if`
Executes a block of code only if a certain condition is `True`.  
**Input**
```liquid
{% if product.title == 'Awesome Shoes' %}
  These shoes are awesome!
{% endif %}
```
**Output**
```
  These shoes are awesome!
```

#### `unless`
The opposite of `if` – executes a block of code only if a certain condition is `not` met.

**Input**
```liquid
{% unless product.title == 'Awesome Shoes' %}
  These shoes are not awesome.
{% endunless %}
```
**Output**
```
These shoes are not awesome.
```

This would be the equivalent of doing the following:
```liquid
{% if product.title != 'Awesome Shoes' %}
  These shoes are not awesome.
{% endif %}
```

#### `elsif(elif, else if) / else`
Adds more conditions within an if or unless block. `liquidpy` recoglizes not only `elsif` keyword as `liquid` does, it also treats `else if` and `elif` as `elsif` in `liquid`, or `elif` in `python`

**Input**

{% if customer.name == 'kevin' %}
  Hey Kevin!
{% elsif customer.name == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}

**Output**
```
  Hey Anonymous!
```

#### `case/when`
Creates a switch statement to compare a variable with different values. case initializes the switch statement, and when compares its values.

**Input**
```liquid
{% assign handle = 'cake' %}
{% case handle %}
  {% when 'cake' %}
     This is a cake
  {% when 'cookie' %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
```

**Output**
```
     This is a cake
```

### Iteration/Loop
Iteration tags run blocks of code repeatedly.  
__`for(parameters)`, `tablerow` and `cycle` are abandoned in `liquidpy`, because they can be easied performed using python expressions__  

#### `while`
__`liquid` doesn't support `while`, but we have it here. Use it just like you are writing `python` codes:__  

**Input**
```liquid
{% assign i = 3 %}
{% while i > 0 %}
{{i}}
{% assign i = i - 1 %}
{% endwhile %}
```
**Output**
```
3
2
1
```

#### `for`
Repeatedly executes a block of code. For a full list of attributes available within a for loop.  

**Input**
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {{ product.title }}
{% endfor %}
```

**Output**
```
  hat
  shirt
  pants
```

#### `break/continue`
Exit the loop or skip current iteration.  

**Input**
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {% if product.title == 'shirt' %}
    {% break %}
  {% endif %}
  {{ product.title }}
{% endfor %}
```

**Output**
```
  hat
```

**Input**
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {% if product.title == 'shirt' %}
    {% continue %}
  {% endif %}
  {{ product.title }}
{% endfor %}
```

**Output**
```
  hat
  pants
```

### Raw
Raw temporarily disables tag processing. This is useful for generating content (eg, Mustache, Handlebars) which uses conflicting syntax.  

**Input**
```liquid
{% raw %}
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
{% endraw %}
```

**Output**
```
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
```

### Variable
#### `assign`
Creates a new variable.  

**Input**
```liquid
{% assign my_variable = false %}
{% if my_variable != true %}
  This statement is valid.
{% endif %}
```

**Output**
```
  This statement is valid.
```

**Input**
```liquid
{% assign foo = "bar" %}
{{ foo }}
```

**Output**
```
bar
```

#### `capture`
Captures the string inside of the opening and closing tags and assigns it to a variable. Variables created through {% capture %} are strings.  

**Input**
```liquid
{% capture my_variable %}I am being captured.{% endcapture %}
{{ my_variable }}
```

**Output**
```
I am being captured.
```

Using capture, you can create complex strings using other variables created with assign.

**Input**
```liquid
{% assign favorite_food = 'pizza' %}
{% assign age = 35 %}
{% capture about_me %}
I am {{ age }} and my favorite food is {{ favorite_food }}.
{% endcapture %}
{{ about_me }}
```

**Output**
```
I am 35 and my favourite food is pizza.
```

#### `increment`
Creates a new number variable, and increases its value by one every time it is called. __The variable has to be initate before `increment`__

**Input**
```liquid
{% assign my_counter = 0 %}
{{my_counter}}
{% increment my_counter %}
{{my_counter}}
{% increment my_counter %}
{{my_counter}}
{% increment my_counter %}
{{my_counter}}
```

**Output**
```
0
1
2
3
```

__NOTE: Unlike `liquid`, Variables created through the increment tag affects variables created through assign or capture.__

#### `decrement`
Creates a new number variable, and decreases its value by one every time it is called.  

**Input**
```liquid
{% assign variable = 0 %}
{% decrement variable %}
{{ variable }}
{% decrement variable %}
{{ variable }}
{% decrement variable %}
{{ variable }}
```

**Output**
```
-1
-2
-3
```

## Filters
`liquidpy` tries to support `liquid` filters, however, to support `python` filters themselves, we put `@` before the filters to mark it as `liquid` filters.  
__`escapse_once`, `sort_natural`, `first` and `last` filters are abandoned.__  

**Where you can use filters**  

- In expression tags: `{{`, `}}` and `{{-`, `-}}`
- In `assign` block: `{% assign a = "abc" | len %}`
- In `case/when` block: 
  ```liquid
  {% case var | len %}
    {% when -3 | @abs %}
      {{Length is 3}}
    {% when 2 %}
      {{Length is 2}}
    {% else %}
      {{Other length}}
  {% endcase %}
  ```  

### `liquid` filters

#### Math filters  
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

#### String filters  
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

#### List/Array filters
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

#### Other filters  
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

### Python filters
#### Direct filters
Any function in the environment that takes the first arguments as the values on the left of the expression (value before `|`) could be used as direct filters:  
```liquid
{{"123" | len}}
{# output: 3 #}

{{ 1.234, 2 | round }}
{# output: 1.23 #}
```

You can even use python expressions on the left:  
```liquid
{{len("123") | @plus: 3}}
{# output: 6 #}

{{ 1.234, 1+1 | round }}
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

#### Getitem filters
You can get the items directly from the values on the left:  
```liquid
{{ [1,2,3] | [0] }}
{# output: 1 #}

{{ [1,2,3] | [1:] | sum }}
{# output: 5 #}

{{ {"a": 1} | ["a"] }}
{# output: 1 #}
```

Remember if you if have multiple values on the left, they will be treated as a `tuple`:  
```liquid
{{ 1.234, 1+1 | [1] }}
{# output: 2 #}
```

#### Attribute filters
Get the value from the attribute of an object. If it is `callable`, you can also use it as a filter:  
```liquid
{{ "," | .join: ['a', 'b'] }}
{# output: a,b #}

{{ "{}, {}!" | .format: "Hello", "world" }}
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

#### Lambda filters
You may also apply lambda filters:  
```liquid
{% python from os import path %}
{{ "/path/to/file.txt" | lambda p, path = path: path.join( path.dirname(p), path.splitext(p)[0] + '.sorted' + path.splitext(p)[1] ) }}
{# output: /path/to/file.sorted.txt #}
```

If you don't have to use global variables in `lambda`, you may also omit the `lambda` keyword:

```liquid
{{ "/path/to/file.txt" | :len(a) - 4 }}
{# output: 13 #}
```
The argument names start from `a`, up to `z`.


[1]: https://shopify.github.io/liquid/
[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
[5]: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
[6]: https://api.codacy.com/project/badge/Grade/ddbe1b0441f343f5abfdec3811a4e482
[7]: https://api.codacy.com/project/badge/Coverage/ddbe1b0441f343f5abfdec3811a4e482
