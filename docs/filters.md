Filters in python mode are more flexible then the ones in standard mode:

- Base value does not have to be the first argument of the filter. One can use `_` as a placeholder for the base value
- Keyword arguments are allowed to call the filter

```python
from liquid import filter_manager_python

@filter_manager_python.register('sum')
def filter_sum(a=1, b=2, c=3):
    return a + b + c
```

To call it with base value as second argument:
```liquid
{{ 4 | filter_sum: 1, _ }} {% comment %} // 1 + 4 + 3 = 8 {% endcomment %}
```

To call it with keyword arguments:
```liquid
{{ 4 | filter_sum: b=1 }} {% comment %} // 4 + 1 + 3 = 8 {% endcomment %}
```

## Liquid filters
`liquidpy` support all Liquid filters. However, for some of them, there is no EmptyDrop object returned. Instead, it returns the object, which is treated empty in python.

For example:
```python
Liquid('{{ x | sort }}').render(x=[])
# x will be an EmptyDrop object if rendered in standard mode, but
# still [] if rendered in python mode
```

## Simple filters
These filters are callable object from python builtins or defined in the template with a simple name.

For example:
```python
Liquid('{{"foo" | len}}', {'mode': 'python'}).render() # // 3
```

One can also pass in a filter:

```python
Liquid('{{"foo" | concat}}', {'mode': 'python'}).render(
  concat = lambda x: x + 'bar'
) # // foobar
```

A filter can be even defined from inside the template:
```python
Liquid("""
{%- assign concat = lambda x: x + 'bar' -%}
{{ "foo" | concat }}""", {'mode': 'python'}).render() # // foobar
```

However, when you have a filter that is not with a simple name, for example, in a list, you have to use a complex filter.

### render

This filter allows one to render a template in pythom mode from inside a template:
```python
LiquidPython('{{ tpl | render }}').render(
    tpl="{{x}}", x=1
) # // '1'
LiquidPython('{{ tpl | render: x=2 }}').render(
    tpl="{{x}}", x=1
) # // '2'
```

## Complex filters

They are nothing but just filters with a `@` modifier, when the filter needs to be computed (ie, an attribute of an object, an element of a list, etc):
```python
from os import path
Liquid(
  '{{ "/path" | @path.join: "to" }}', {'mode': 'python'}
).render(path=path) # //  /path/to
```

```python
from os import path
filters = [path.join]
Liquid(
  '{{ "/path" | @filters[0]: "to" }}', {'mode': 'python'}
).render(filters=filters) # //  /path/to
```

Since the base value from the output tag (`{{ ... }}`) can also be an iterable or a dictionary, we also support `*` and `**` modifiers for simple and complex filters to expand the values:

```python
from os import path
Liquid(
  '{{ ("/path", "to") | *@path.join }}', {'mode': 'python'}
).render(path=path) # //  /path/to
```

```python
Liquid('''
  {% assign add = lambda a, b: a + b %}
  {{ {"a": 1, "b": 2} | **add }}
''', {'mode': 'python'}).render() # // 3
```

For filters in standard mode, the single base value has to be passed as the first argument of the filter. However, in python mode, you can specify it explictly in a different position:

```python
from os import path
Liquid('''
  {{ "to" | @path.join: "/path", _ }}'
''', {'mode': 'python'}).render(path=path) # //  /path/to
```

The underscore changes the position of the base value (`"to"`) from the first argument to the second. Without it, we will get `to//path`

!!! Note

    The base value placeholder (`_`) doesn't work with expanding modifiers (`*`, `**`) when you have an iteratable value or a dictionary-like object as the base value.

## Dot filters/Attribute filters

Sometimes, we also want to use the attribute of the base value as a filter, since it can be a callable too. For example:
```python
Liquid('{{ ", " | .join: ["a", "b", "c"] }}',
       {'mode': 'python'}).render() # // a, b, c
```

You could even access some magic methods:
```python
Liquid('{{ "foo" | .__len__ }}', {'mode': 'python'}).render()
# // 3
```

!!! Tip

    To get an attribute as a value from an object, you can use `getattr` filter:
    ```python
    from pathlib import Path
    LiquidPython('{{ path | getattr: "stem"}}').render(
      path=Path('a/b/c.txt')
    )
    # // c
    ```

## Subscript filters

Similar to dot filters, sometimes, we also want to use the callables that are accessed by subscriptting the base value:
```python
Liquid('{{ base | [0] }}',
       {'mode': 'python'}).render(
         base: [lambda: 'Hello']
       ) # // Hello
```

To get the first element of the list:
```python
Liquid('{{ base | .__getitem__: 0 }}',
       {'mode': 'python'}).render(
         base=['Hello']
       ) # // Hello
```

Or you can also use the shortcut:
```python
LiquidPython('{{ base | getitem: 0 }}').render(
    base=['Hello']
) # // Hello
```

## Ternary filters

We also support ternary filters in python mode. The syntax is like:
```liquid
{{ base | [filter] ? [filter|constant] ! [filter|constant] }}
{#        ^^^^^^^^   ^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^ #}
{#        part1      part2               part3             #}
```

You can use a filter for `part1` to modify the base value, which will then be the condition value for the ternary filter. `part2` could either be a filter to modify the base value when the condition value is True or just constant, including numbers, strings, None, True or False. It is the same for `part3` when condition value is False.

All the three parts marked above are optional.
When `part1` is not give, it will use the base value itself as the condition value. When `part2` is not given, it will return the base value, same for `part3`.

So theoriatially, you can (but are not recommended to) write something like:
```liquid
{{ base | ? ! }}
```
It basically means tell me if base is True or not. If it is True, return base value, and if it is False, return the base value, too.

Arguments are supported for the filters, for example:

```python
tpl = '{{ base | isinstance: int ? | plus: 1 | append: ".liquid"}}'
Liquid(tpl, {'mode': 'python'}).render(base=1) # // 2
Liquid(tpl, {'mode': 'python'}).render(base="1") # // 1.liquid
```

## Lambda filters

If all of the above filters don't meet your needs, you can also use lambda filters, which allow you to operate the base value pretty arbitrarily:

```python
tpl = '{{ base | lambda a: a ** 2 }}'
Liquid(tpl, {'mode': 'python'}).render(base=3) # // 9
```
