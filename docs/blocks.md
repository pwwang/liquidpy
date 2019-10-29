
# Comment
__Unlike `liquid`, `liquidpy` has two comment systems: comment block `{% comment %}...{% endcomment %}` and comment tag `{# ... #}`.__
__The former one is also supported by `liquid`, but acts differently. In `liquid`, anything between the comment block will be igored. However, it turns to python comments in `liquidpy`. If you want the comments to be ignore, you should use comment tag instead:__

<div markdown="1" class="two-column">

Input:
```liquid
Anything you put between
{% comment %}
and
{% endcomment %}
tags is turned into a comment.
```

</div>
<div markdown="1" class="two-column">

Output:
```
Anything you put between
# and
tags is turned into a comment.
```

</div>

---

<div markdown="1" class="two-column">

```liquid
Anything you put between
{# and #}
tags is turned into a comment.
```

</div>
<div markdown="1" class="two-column">

```
Anything you put between
tags is turned into a comment.
```

</div>

---

Use a different comment sign:

<div markdown="1" class="two-column">

```liquid
{% comment // %}
This
will be
translated
as comments
{% endcomment %}
```

</div>
<div markdown="1" class="two-column">

```
// This
// will be
// translated
// as comments
```

</div>


---

Use a comment wrapper:

<div markdown="1" class="two-column">

```liquid
{% comment /* */ %}
This
will be
translated
as comments
{% endcomment %}
```

</div>
<div markdown="1" class="two-column">

```
/* This */
/* will be */
/* translated */
/* as comments */
```

</div>

---

# Python source
__You may also insert python source code to the template, one line each time__

<div markdown="1" class="two-column">

Input:
```liquid
{% mode compact %}
{% python from os import path %}
{% python from glob import glob %}
{% python d = './date' %}
{% for filepath in glob(path.join(d, '*.txt')) %}
  {{path.basename(filepath)}}
{% endfor %}

```

</div>
<div markdown="1" class="two-column">

Output:
```
  a.txt
  b.txt
```

</div>

---
<div markdown="1" class="two-column">

Input:
```liquid
{% mode compact %}
{% import os %}
{% from glob import glob %}
{% python d = './date' %}
{% for filepath in glob(os.path.join(d, '*.txt')) %}
  {{os.path.basename(filepath)}}
{% endfor %}

```

</div>
<div markdown="1" class="two-column">

Output:
```
  a.txt
  b.txt
```

</div>

---

# Control flow
## `if`
Executes a block of code only if a certain condition is `True`.

<div markdown="1" class="two-column">

Input:
```liquid
{% if product.title == 'Awesome Shoes' %}
  These shoes are awesome!
{% endif %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  These shoes are awesome!
```

</div>

You can also use `liquidpy` expressions (`{{ ... }}`) in the conditions, but you have to use backticks to quote them. For example:
```liquid
{% if `product.title | .lower:` == 'awesome shoes' %}
  These shoes are awesome!
{% endif %}
```

!!! note:

    We support "dot" operation to get the value of a key from dictionaries. For example: `Liquid("{{a.x}}").render(a = {"x": 1})`. However, when you use it in `if/unless/while` conditions, you have to use backticks to quote it.

---

## `unless`
The opposite of `if` – executes a block of code only if a certain condition is `not` met.

<div markdown="1" class="two-column">

Input:
```liquid
{% unless product.title == 'Awesome Shoes' %}
  These shoes are not awesome.
{% endunless %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
These shoes are not awesome.
```

</div>

---

This would be the equivalent of doing the following:
```liquid
{% if product.title != 'Awesome Shoes' %}
  These shoes are not awesome.
{% endif %}
```

## `elsif(elif, elseif, else if) / else`
Adds more conditions within an if or unless block. `liquidpy` recoglizes not only `elsif` keyword as `liquid` does, it also treats `else if` and `elif` as `elsif` in `liquid`, or `elif` in `python`

<div markdown="1" class="two-column">

Input:
```liquid
{% if customer.name == 'kevin' %}
  Hey Kevin!
{% elsif customer.name == 'anonymous' %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  Hey Anonymous!
```

</div>

---

## `case/when`
Creates a switch statement to compare a variable with different values. case initializes the switch statement, and when compares its values.

<div markdown="1" class="two-column">

Input:
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

</div>
<div markdown="1" class="two-column">

Output:
```
     This is a cake
```

</div>

---

# Iteration/Loop
Iteration tags run blocks of code repeatedly.
__`for(parameters)`, `tablerow` and `cycle` are abandoned in `liquidpy`, because they can be easied performed using python expressions__

## `while`
__`liquid` doesn't support `while`, but we have it here. Use it just like you are writing `python` codes:__

<div markdown="1" class="two-column">

Input:
```liquid
{% assign i = 3 %}
{% while i > 0 %}
{{i}}
{% assign i = i - 1 %}
{% endwhile %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
3
2
1
```

</div>

---

## `for`
Repeatedly executes a block of code. For a full list of attributes available within a for loop.

<div markdown="1" class="two-column">

Input:
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {{ product.title }}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  hat
  shirt
  pants
```

</div>

---
<div markdown="1" class="two-column">

Input (forloop object support):
See: https://help.shopify.com/en/themes/liquid/objects/for-loops
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {% if forloop.first %}
  {{ product.title }}
  {% endif %}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  hat
```

</div>

---

## `break/continue`
Exit the loop or skip current iteration.

<div markdown="1" class="two-column">

Input:
```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {% if product.title == 'shirt' %}
    {% break %}
  {% endif %}
  {{ product.title }}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  hat
```

</div>

---

<div markdown="1" class="two-column">

```liquid
{# collection.products = [Product(title = 'hat'), Product(title = 'shirt'), Product(title = 'pants')] #}
{% for product in collection.products %}
  {% if product.title == 'shirt' %}
    {% continue %}
  {% endif %}
  {{ product.title }}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

```
  hat
  pants
```

</div>

---

# Raw
Raw temporarily disables tag processing. This is useful for generating content (eg, Mustache, Handlebars) which uses conflicting syntax.

<div markdown="1" class="two-column">

Input:
```liquid
{% raw %}
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
{% endraw %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  In Handlebars, {{ this }} will be HTML-escaped, but
  {{{ that }}} will not.
```

</div>

---

# Variable
## `assign`
Creates a new variable.

<div markdown="1" class="two-column">

Input:
```liquid
{% assign my_variable = false %}
{% if my_variable != true %}
  This statement is valid.
{% endif %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  This statement is valid.
```

</div>

---

<div markdown="1" class="two-column">

```liquid
{% assign foo = "bar" | @append: "foo" %}
{{ foo }}
```

</div>
<div markdown="1" class="two-column">

```
barfoo
```

</div>

---

## `capture`
Captures the string inside of the opening and closing tags and assigns it to a variable. Variables created through {% capture %} are strings.

<div markdown="1" class="two-column">

Input:
```liquid
{% capture my_variable %}I am being captured.{% endcapture %}
{{ my_variable }}
```

</div>
<div markdown="1" class="two-column">

Output:
```
I am being captured.
```

</div>

---

Using capture, you can create complex strings using other variables created with assign.

<div markdown="1" class="two-column">

Input:
```liquid
{% assign favorite_food = 'pizza' %}
{% assign age = 35 %}
{% capture about_me %}
I am {{ age }} and my favorite food is {{ favorite_food }}.
{% if false %}Something you dont't want{% endif %}
{% endcapture %}
{{ about_me }}
```

</div>
<div markdown="1" class="two-column">

Output:
```
I am 35 and my favourite food is pizza.
```

</div>

---

## `increment`
Creates a new number variable, and increases its value by one every time it is called. __The variable has to be initate before `increment`__

<div markdown="1" class="two-column">

Input:
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

</div>
<div markdown="1" class="two-column">

Output:
```
0
1
2
3
```

</div>

---

!!! note
	__Unlike `liquid`, Variables created through the increment tag affects variables created through assign or capture.__

## `decrement`
Creates a new number variable, and decreases its value by one every time it is called.

<div markdown="1" class="two-column">

Input:
```liquid
{% assign variable = 0 %}
{% decrement variable %}
{{ variable }}
{% decrement variable %}
{{ variable }}
{% decrement variable %}
{{ variable }}
```

</div>
<div markdown="1" class="two-column">

Output:
```
-1
-2
-3
```

</div>

---
