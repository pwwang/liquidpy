
You may checkout the documentation for standard liquid:
- https://shopify.github.io/liquid/

`liquidpy` tries to maintain the maximum compatibility with `liquid`. But we do have some differences:

- [Filter] `round()` always returns a `float` rather than an `integer` when `ndigits=0`
- [Operator] The logical operators `and`/`or` collapse from left to right (it's right to left in `liquid`)
    - See: https://shopify.github.io/liquid/basics/operators/#order-of-operations
- [Truthy and falsy] Instead of always truthy for empty string, 0, empty array, they are falsy in `liquidpy`
- [Iteration] Literal ranges (`(1..5)`) are suported by `liquidpy`. However, the start and the stop must be integers or names, meaning this is not supported `(1..array.size)`. You can do this instead:

    ```liquid
    {% assign asize = array.size %}
    {% for i in (1..asize) %}
    ...
    {% endfor %}
    ```
