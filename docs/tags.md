
Except for the tags introducted in [Additional Tags](../additional-tags), python mode also support following tags, some of which act exactly the same as the ones from standard mode, but some not.

## Comment

Any content in `{# ... #}` will be intepreted as a comment, and will be ignored in rendering. It works like a shortcut for `{% comment %} ... {% endcomment %}` with the difference that no other tags allowed inside `{# ... #}`

It also has whitespace-control verions:
```liquid
{#- ...  #}  {# Right whitespaces of prior literals are trimmed #}
{#  ... -#}  {# Left whitespaces of next literals are trimmed #}
{#- ... -#}  {# Right whitespaces of prior literals and #}
             {# left whitespaces of next literals are trimmed #}
```

## Control flow
### if

Executes a block of code only if a certain condition is True

```liquid
{% if condition %}
Executed when condition is True
{% endif %}
```

Filters are also allowed for the `condition`:
```liquid
{% if condition | filter: args | another_filter: args %}
...
{% endif %}
```

### unless

Executes a block of code only if a certain condition is False

It's equvalent to `{% if not (condition) %}`

### else/elsif/elif/else if

Adds more conditions within if/unless block.

`else` also works with [`for`](#for) and [`while`](#while) blocks

`elif` is an alias for `elseif` to make it more like a python syntax

`else if` works the same as `elif/elsif`.

```liquid
{% if customer.name == "kevin" %}
  Hey Kevin!
{% elif customer.name == "anonymous" %}
  Hey Anonymous!
{% else %}
  Hi Stranger!
{% endif %}
```

### case/when

Creates a switch statement to compare a variable with different values. case initializes the switch statement, and when compares its values.
```liquid
{% assign handle = "cake" %}
{% case handle %}
  {% when "cake" %}
     This is a cake
  {% when "cookie" %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
```
Filters are also allowed for `case` and `when` tag.

## Iteration

`tablerow` tag is abandoned in python mode

### for

`for` tag works a little differently than it does in standard mode. We don't have `forloop` object inside the block, but we enable multiple-variable iteration and filters in the variable to loop over:

No parameters are allowed for `for` tag like in standard mode.

```liquid
{% for key, val in d.items(): %}
...
{% endfor %}
```

```liquid
{% for i, elem in elements | enumerate %}
...
{% endfor %}
```

`{% else %}` is also allowed within the block, which works just like the `for ... else` pair in python.

### while

Works similar to `for`. Filters are allowed, and with `{% else %}`, it works like the `while ... else` pair in python.

```liquid
{% assign a = 10 %}
{% while a %}
    a is now: {{a}}
    {% if a == 3 %}
        {% break %}
    {% endif %}
    {% assign a = a - 1 %}
{% endwhile %}
```

### cycle
Works the same as it in standard mode. See [cycle](https://shopify.github.io/liquid/tags/iteration/#cycle).

## Raw
`raw` tag works exactly like it in standard mode. See [raw](https://shopify.github.io/liquid/tags/raw/)

## Variable

### assign
Creates or modifies a new variable.

Filters allowed for the value.

!!! Note

    Variables created by this tag is only available in the same block where it is defined. But the variable it modifies is still available in the block where it is initially defined.

### capture
Works the same as it does in standard mode. See [capture](https://shopify.github.io/liquid/tags/variable/#capture).

### increment
Works the same as it does in standard mode. See [increment](https://shopify.github.io/liquid/tags/variable/#increment)

### decrement
Works the same as it does in standard mode. See [decrement](https://shopify.github.io/liquid/tags/variable/#decrement)

## Python-related tags

### python
A block to execute python codes.

!!! Danger

    Arbitrary codes may be executed in the block, so it is not allowed when `strict` is True. Use it only when you know what will be executed.

- Single-line code:
    ```liquid
    {% python func = lambda a: a+1 %}
    ```

- Multiple-line code:
    ```liquid
    {% python %}
    def func(a):
        return a + 1
    {% endpython %}
    ```
    You may also include other tags in the multi-line python tag:
    ```liquid
    {% python %}
        {% if x | isinstance: int %}
        def func(a):
            return a + 1
        {% else %}
        def func(a):
            return a + ' is a string.'
        {% endif %}
    {% endpython %}
    ```

### import

A shortcut for `{% python import ... %}` to import packages/modules from python

```liquid
{% import os %}
```

!!! Danger

    `import` tag is not allowed when `strict` is True.

### from

A shortcut for `{% python from ... import ... %}` to import packages/modules from python

```liquid
{% from os import path %}
```

!!! Danger

    `from` tag is not allowed when `strict` is True.

## Config

See [Configuration](../configuration)
