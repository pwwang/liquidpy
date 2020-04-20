
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
{% config mode=compact %}
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
{% config mode=compact %}
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

We can also add a block of python code:

<div markdown="1" class="two-column">

Input:
```liquid
{% config mode=compact %}
{% python %}
import os
from glob import glob
d = './date'
{% endpython %}
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

!!! note

    For python block, you must start your code without any indentations

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

!!! note

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

!!! note

    If `product` is an object with attributes `title` then the above codes are Okay. However, if `product` is a dictionary, and `title` can only be accessed by `product['title']`, then you can do `{% unless product['title'] == 'Awesome Shoes' %}` or simply `{% unless `product.title` == 'Awesome Shoes' %}`

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
{# collection.products = [Product(title = 'hat'),
                          Product(title = 'shirt'),
                          Product(title = 'pants')] #}
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
{# collection.products = [Product(title = 'hat'),
                          Product(title = 'shirt'),
                          Product(title = 'pants')] #}
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
<div markdown="1" class="two-column">

Input (cycle support):
See: https://help.shopify.com/en/themes/liquid/tags/iteration-tags#cycle
```liquid
{% for i in range(10) %}
  {% cycle "a", "b", "c" %}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
abcabcabca
```

</div>

---
<div markdown="1" class="two-column">

Input (You can also use variables):
```liquid
{% assign group = ["a", "b", "c"] %}
{% for i in range(10) %}
  {% cycle group %}
{% endfor %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
abcabcabca
```

</div>

---

!!! note

    - `cycle` doesn't have group argument as it from `liquid` does.
    - No `from` or `with` keyword needed for `cycle` to work with variables
    - Comma `, ` should be used instead of space(` `) for arguments

## `break/continue`
Exit the loop or skip current iteration.

<div markdown="1" class="two-column">

Input:
```liquid
{# collection.products = [Product(title = 'hat'),
                          Product(title = 'shirt'),
                          Product(title = 'pants')] #}
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
{# collection.products = [Product(title = 'hat'),
                          Product(title = 'shirt'),
                          Product(title = 'pants')] #}
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
Captures the string inside of the opening and closing tags and assigns it to a variable. Variables created through `{% capture %}` are strings.

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

# Write you only statement node

Since `v0.5.0`, `liquidpy` support definition of your own statement node.

There are two types of statement nodes (nodes for short) in `liquidpy`. Void nodes (nodes that do need and end node to close, i.e. `{% config ... %}`) and non-void nodes (nodes that need end node to close, i.e. `{% if ... %}...{% endif %}`)

## Void node
To write a void node, you just need to subclass the `NodeVoid` class. For example, here we create a new node called `cmd` or `command` to capture the output of command:

```python
from contextlib import suppress
from liquid.nodes import NodeVoid, register_node
from liquid.defaults import LIQUID_RENDERED_APPEND
from liquid.exceptions import LiquidSyntaxError, LiquidCodeTagExists

class NodeCommand(NodeVoid):

    def start(self):
        """Check if the node is in right format,
        and do some preparation for parsing"""

        # attrs is the rest string of the node other than name
        if not self.attrs:
            # the context has the filename, lineno, etc
            raise LiquidSyntaxError("Empty command", self.context)

    def parse_node(self):
        # log the parsing process
        super().parse_node()

        # let us just do a simple version, using subprocess.check_output
        # import the module, since this module will be import just once,
        # so we put it in the shared_code
        with suppress(LiquidCodeTagExists), \
                self.shared_code.tag('import_subprocess') as tagged:
            tagged.add_line("import subprocess")

        # use it to parse the command
        # save the result to a variable first
        # add id here to avoid conflicts
        self.code.add_line(f"command_{id(self)} = subprocess.check_output("
                           f"['bash', '-c', {self.attrs!r}], encoding='utf-8')")
        # put the results in rendered content
        self.code.add_line(f"{LIQUID_RENDERED_APPEND}(command_{id(self)})")

# register the node
register_node("command", NodeCommand)
# add an alias
register_node("cmd", NodeCommand)
```

See how it works:
```python
>>> from liquid import Liquid
>>> # import your NodeCommand definitions
>>> print(Liquid("{% command ls %}").render())
LICENSE
README.md
README.rst
api.py
docs
liquid
mkdocs.yml
poetry.lock
pyproject.toml
pyproject.toml.bak
requirements.txt
setup.py
tests
tox.ini

```

## Non-void node

Let's define a simple `foreach` node to implement following (mimic the `foreach` in `php`):
```
{% foreach <list> as <element> %}
{% endforeach %}

{% foreach <list> as <index>, <element> %}
{% endforeach %}

{% foreach <dict> as <key>, <value> %}
{% endforeach %}
```

```python
import attr
from liquid.nodes import Node, register_node
from liquid.exceptions import LiquidSyntaxError

# if we have extra attributes, we need
@attr.s(kw_only=True)
class NodeForeach(Node):

    parts = attr.ib(init=False, default=attr.Factory(list))

    def start(self):
        """Check if the node is in right format,
        and do some preparation for parsing"""

        # attrs is the rest string of the node other than name
        if not self.attrs:
            # the context has the filename, lineno, etc
            raise LiquidSyntaxError("Empty foreach node", self.context)

        self.parts = [attr.strip() for attr in self.attrs.split(' as ')]
        if len(self.parts) != 2:
            raise LiquidSyntaxError("Exactly one 'as' required in foreach node",
                                    self.context)
        # allow python and liquid expressions
        self.parts[0] = self.try_mixed(self.parts[0])
        variables = [part.strip() for part in self.parts[1].split(',')]
        if len(variables) > 2:
            raise LiquidSyntaxError("At most 2 variables to extract in foreach",
                                    self.context)
        # TODO: check if variables are valid identifiers
        self.parts[1:] = variables

    def parse_node(self):
        # log the parsing process
        super().parse_node()

        # we need to convert it to python's for loop
        # we need to know if the first part is a list or a dictionary
        varname = f"liquid_foreach_{id(self)}"
        self.code.add_line(f"{varname} = {self.parts[0]}")
        # get the right part in python for loop
        self.code.add_line(f"{varname} = enumerate({varname}) "
                           f"if isinstance({varname}, list) "
                           f"else ({varname}).items()")
        # add the for loop
        variables = ','.join(self.parts[1:])
        self.code.add_line(f"for {variables} in {varname}:")
        # indent for future codes
        self.code.indent()

    def end(self, name):
        # we need to match the name
        super().end(name)
        # we need to dedent, since codes inside foreach has been added
        self.code.dedent()

# register the node
register_node("foreach", NodeForeach)
```

See how it works:
```python
>>> liq = Liquid("""{% foreach lang_to_ext as lang, ext %}
... {{lang}} -> {{ext}}
... {% endforeach %}""")
>>> print(liq.render(lang_to_ext=dict(php=".php", python=".py", javascript=".js")))

php -> .php

python -> .py

javascript -> .js

```

### Intact node

Sometimes we don't want to content between `{% raw %}` and `{% endraw %}` to be parsed as liquid template, then we just need to subclass `NodeIntact` and use `parse_content` to parse it.

See how `raw` node was defined in `liquid/nodes.py`
