One can extend `liquidpy` in both modes by adding or removing tags and filters.

## Registering tags
To define a new tag, one should subclass the `Tag` class (`TagPython` for tags in python mode).

```python
from liquid import Tag, tag_manager

@tag_manager.register
class TagEcho(Tag):
    # the start rule
    START = 'tag_echo'
    # the grammar based on the base_grammar
    GRAMMAR = 'tag_echo: output'

    def parse(self, force=False):
        # Use the default parser to parse the output rule
        return super().parse(force)

    def _render(self, local_vars, global_vars):
        # render the parsed rule
        return self.parsed.render(local_vars, global_vars)
```

You would like to check grammar for lark-parser, as well as the base grammar at `tags/grammar.lark` or `python/tags/grammar.lark` for python mode

Also check the implementation for the bulting tags.

The above tag implements the same function as the output tag `{{ ... }}` by `{% echo ... %}`.

To register the tag with different names, you can add names to the `tag_manager.register` function:
```python
@tag_manager.register('print, echo') # or
@tag_manager.register(['print', 'echo']) # or
```
Then you can do `{% print ... %}` or `{% echo ... %}`

To create and register a tag for python mode:
```python
from liquid import tag_manager, TagPython

@tag_manager.register(mode='python')
class TagEcho(TagPython):
    ...

# or
from python import tag_manager_python, TagPython

@tag_manager_python.register
class TagEcho(TagPython):
    ...
```

## Unregistering tags

If you want to unregister/disable a tag:
```python
tag_class = tag_manager.unregister('echo')
```
The class is returned from unregister function, which, later on, in a case you want to register it back:
```python
tag_manager.register('echo')(tag_class)
```

!!! Note

    If you registered a tag with multiple names (say `echo` and `print`), and only unregistered `echo`, then `print` tag is still avaliable in the template.

    To unregister both of them:
    ```python
    tag_manager.unregister('echo')
    tag_manager.unregister('print')
    ```

If you want to do this for python mode, use `tag_manager_python` or `tag_manager.register(..., mode='python')`/`tag_manager.unregister(..., mode='python')`

## Registering filters

Filters are just functions:

```python
from liquid import filter_manager

@filter_manager.register
def incr(base, inc=1):
    return base + inc
```

```liquid
{{ 1 | incr }} {% comment %} // 2 {% end comment%}
{{ 1 | incr: 2 }} {% comment %} // 3 {% end comment%}
```

Similar to tag register, filters can also be registered with different names:
```python
from liquid import filter_manager

@filter_manager.register('increment')
def incr(base, inc=1):
    return base + inc

# use it in template:
# {{ 1 | increment }}
```

For standard mode, the base value has to be the first argument of a filter.

But for python mode, filters are more flexible. For the above filter, to register it for python mode:
```python
@filter_manager.register(mode='python') # or

from liquid import filter_manager_python
@filter_manager_python.register
```

It is available to pass the base value as the second argument:
```liquid
{{ 2 | incr: 1, _}} {% comment %} // 3 {% end comment%}
```

See [filters](../filters) for more information.

Additionally, in python mode, callables in locals/globals are also available working as filters
```liquid
{{ "foo" | len }} {% comment %} // 3 {% end comment%}
```

One can also define a lambda function in the template to work as a filter:
```liquid
{% assign len_plus_1 = lambda x: len(x) + 1 %}
```
```liquid
{{ "foo" | len_plus_1 }} {% comment %} // 4 {% end comment%}
```

## Unregistering filters

Same as tag unregister, a function is returned from `filter_manager.unregester` for later re-register.

!!! Warning

    Unregistering a filter in python model is only available for the filters registered by `filter_manager` or `filter_manager_python`.
