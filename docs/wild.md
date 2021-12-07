Wild mode tries to introduce more flexiblities for the template. It's very arbitrary for one to do things inside the template. So security is not it's first priority.

!!! Warning

    Do not trust any templates in wild mode with `liquidpy`

Below are some features it supports.

## Globals

- By default, wild mode loads all `__builtins__` as global variables, except those whose names start with `_`.
- `nil` is also loaded and intepreted as `None`.
- Other globals if not overridden by the above:
    - See: https://jinja.palletsprojects.com/en/3.0.x/templates/?highlight=builtin%20filters#list-of-global-functions

## Filters

- All builtin functions are loaded as filters, except those whose names starts with `_` and not in: `"copyright", "credits", "input", "help", "globals", "license", "locals", "memoryview", "object", "property", "staticmethod", "super"`.
- Filters from standard mode are loaded
- Builtin jinja filters are enabled if not overridden by the above filters
    - See: https://jinja.palletsprojects.com/en/3.0.x/templates/?highlight=builtin%20filters#builtin-filters
- `ifelse`:
    - See: https://pwwang.github.io/liquidpy/api/liquid.filters.wild/
- `map()`
    - It is overridden by python's `builtins.map()`. To use the one from `liquid`, try `liquid_map()`

## Tests

All jinja tests are supported

See: https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-tests

## Tags

`liquidpy` wild mode supports a set of tags that we can do arbitrary things.

### `python` tag

The `python` tag allows you to execute arbitrary code inside a template. It supports single line mode and block mode.

If you just want execute a single line of python code:

```liquid
{% python a = 1 %}
```

Or if you want to execute a chunk of code:
```liquid
{% python %}
def func(x)
    ...
b = func(a)
{% endpython %}
```

!!! Note

    The `python` tag can only interact with the global variables. The variables in the context (`Context.vars`) cannot be referred and will not be affected.

In the above examples, the first will write variable `a` the `environment.globals` or overwrite it.
The second will use variable `a` in `environment.globals` and then write `b` to it.

!!! Tip

    Any variables declared at top level of the code gets stored in the `environment.globals`. If you don't want some to be stored, you should delete them using `del`

!!! Tip

    The code will be dedentated using `textwrap.dedent` and then send to `exec`. So:
    ```liquid
    {% python %}[space][space]a
    [space][space]b
    {% endpython %}
    ```
    works as expected. But you can also write it like this:
    ```liquid
    {% python %}
    [space][space]a
    [space][space]b
    {% endpython %}
    ```
    The first non-spaced line will be ignored.

!!! Tip

    You can also print stuff inside the code, which will be parsed as literals.

### `import_` and `from_` tags

The `import_` and `from_` tags help users to import python modules into the `environment.globals`.
It works the same as python's `import` and `from ... import ...`

!!! Note

    The `import` and `from` from jinja are kept and work as they are in jinja.

### `addfilter` tag

This allows one to add a filter using python code. For example:

```liquid
{% addfilter trunc %}
def trunc(string, n):
    return string[:n]
{% endaddfilter %}
{{ a | trunc: 3 }}
```
When render with `a="abcde"`, it gives: `'abc'`

Like the `python` tag, you can only use the variables in `environment.globals` inside the code.
But unlike the `python` tag, anything you print inside the code will be ignored.

You can also define a filter with the environment:

```liquid
{% addfilter render pass_env %}
def render(env, expr, **kwargs):
    compiled = env.compile_expression(expr)
    return compiled(**kwargs)
{% endaddfilter %}
{{ "item | plus(1)" | render: a }}
```

When render with `a=1`, it gives `2`.

!!! Note
    The expresison passed to `env.compile_expression()` has to use the jinja-supported syntax (i.e. using colon to separate filter and its arguments is not supported).

This is useful when you want to render an template expression insdie the template.

## Extensions

- `jinja2.ext.debug` is enabled
