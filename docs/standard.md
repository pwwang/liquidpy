
You may checkout the documentation for standard liquid:
- https://shopify.github.io/liquid/

`liquidpy` tries to maintain the maximum compatibility with `liquid`. But we do have some differences:

## Filter `round()`

It always returns a `float` rather than an `integer` when `ndigits=0`


## Logical operators

The logical operators `and`/`or` collapse from left to right (it's right to left in `liquid`)

See: https://shopify.github.io/liquid/basics/operators/#order-of-operations


## Truthy and falsy

Instead of always truthy for empty string, 0, empty array, they are falsy in `liquidpy`


## Iteration

Literal ranges (`(1..5)`) are suported by `liquidpy`. However, the start and the stop must be integers or names, meaning this is not supported `(1..array.size)`. You can do this instead:

```liquid
{% assign asize = array.size %}
{% for i in (1..asize) %}
...
{% endfor %}
```

## Typecasting

You are able to do the following in ruby liquid:
```liquid
{{ "1" | plus: 1}}  # 2
```
However, this is not valid in liquidpy. Because the template is eventually compiled into python code and the type handling is delegated to python, but "1" + 1 is not a valid python operation.

So you have to do typecasting yourself:
```liquid
{{ "1" | int | plus: 1 }}  # 2
```

In order to make it work, extra filters `int`, `float`, `str` and `bool` are added as builtin filters. They are also added as globals in order to get this work:
```liquid
{% capture lst_size %}4{% endcapture %}
{{ 2 | at_most: int(lst_size) }}  # 2
```

See also: https://github.com/pwwang/liquidpy/issues/40
