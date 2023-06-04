## Mode of a template

`liquidpy` supports 4 modes:

- standard
    - try to be compatible with standard liquid template engine
    - See: https://shopify.github.io/liquid/
- jekyll
    - try to be compatible with jekyll liquid template engine
    - See: https://jekyllrb.com/docs/liquid/
- shopify
    - try to be compatible with shopify-extended liquid template engine
    - See: https://shopify.dev/api/liquid
- wild
    - With some wild features supported (i.e. executing python code inside the template)
    - See: https://pwwang.github.io/liquidpy/wild

See also an introduction about liquid template engine variants:

- https://shopify.github.io/liquid/basics/variations/

By default, `liquidpy` uses the `standard` mode. But you can specify a mode using the `mode` argument of `Liquid` constructor or `Liquid.from_env()` method.

You can changed the default by:
```python
from liquid import defaults
defaults.MODE = 'wild'
```
before you initialize a `Liquid` object.

## Preset globals and filters

If you want to send a set of global variables and filters to the templates:

```python
from liquid import Liquid, defaults
defaults.FROM_FILE = False

a = 1
b = 2

Liquid("{{a | plus: b}}", globals=globals()).render()
# '3'
```

Specify predefined filters:

```python
import os
from liquid import Liquid, defaults
defaults.FROM_FILE = False

Liquid("{{'/a' | path_join: 'b'}}", filters={'path_join': os.path.join}).render()
# '/a/b'
```

## Relationship with Jinja2/3

Most features here are implemented by jinja extensions. Some of them, however, are impossible to implement via extensions. So we monkey-patched jinja to be better compatible with liquid syntax.

!!! Note

    If you want jinja to work as its original way, remember to unpatch it before you parse and render your template:

    ```python
    from jinja2 import Template
    from liquid import Liquid, patch_jinja, unpatch_jinja

    liq_tpl = Liquid(...)
    liq_tpl.render(...) # works

    jinja_tpl = Template(...) # error may happen
    jinja_tpl.render(...) # error may happen

    unpatch_jinja() # restore jinja
    jinja_tpl = Template(...) # works
    jinja_tpl.render(...) # works

    liq_tpl.render(...) # error may happen

    patch_jinja() # patch jinja again
    liq_tpl.render(...) # works
    ```

Most jinja features are supported unless the filters/tags are overriden. For example, the `round()` filter acts differently then the one in `jinja`.

We could say that the implementations of `liquid` and its variants are super sets of them themselves, with some slight compatibility issues (See `Compatilities` below.)

## Whitespace control

The whitespace control behaves the same as it describes here:

- https://shopify.github.io/liquid/basics/whitespace/

## Compatibilies

See the compatiblity issues for truthy/falsy, tags, and other aspects on pages:

- Standard: https://pwwang.github.com/liquidpy/standard
- Jekyll: https://pwwang.github.com/liquidpy/jekyll
- Shopify: https://pwwang.github.com/liquidpy/shopify

## Wild mode

You can do arbitrary things with the wild mode, like executing python code and adding custom filters inside the template.

See details on:

- https://pwwang.github.com/liquidpy/wild

## `*` modifier for `{{` to keep initial indention along multiple lines

```python
tpl = """\
if True:
    {{* body }}
"""
body = """\
print('hello')
print('world')
"""
print(Liquid(tpl, from_file=False).render(body=body))
```

```
if True:
    print('hello')
    print('world')
```
