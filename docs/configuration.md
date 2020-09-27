## Configuration from Liquid constructor

Initial configurations can be set via `liquid_config` argument:

```python
Liquid(template,
       liquid_config={'item1': 'value1', 'item2': 'value2', ...},
       **envs)
```

Avaiable items are:

- `mode`: Specify the mode of the engine, either `standard` or `python`.
- `strict`: If True, some insecure tags, where potentially arbitrary code can be run, will not be allowed, including `config`, `python`, `from` and `import`.
- `debug`: Show debug information for parsing and rendering the template.
- `extends_dir`: A list of base directories to find the relative path of parent templates specified in `extends` tag. First directory has the highest priority.
- `include_dir`: Similar to `extends_dir`, but for `include` tag.

## Configuration from config tag

One can also override some of the configuration items with a `config` tag in a template:

```liquid
{% config item1=value1 item2=value2 ... %}
```

If you want to set an item to True, then you can omit the value part, like this:
```liquid
{% config item1 item2 %}
```

Configuration item `strict` is NOT allowed to overriden in `config` tag. And `extends_dir` and `include_dir` support only single value instead of a list. `debug` only affects the template where the `config` tag is located.

!!! Note

    Only constants are allowed for the values (numbers, strings, None (nil), True (true), and False (false))
