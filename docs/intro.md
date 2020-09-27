`liquidpy` is compatible with [standard liquid template engine][1]. Variations such as Shopify and Jekyll are not fully supported yet.


Other than that, we have some additional tags supported, including block, include, extends and config.

We also have a python mode to support syntax more close to python.

To check the documentation for standard liquid template engine, see [here][1]. For additional tags to the standard mode, see [Additional Tags](../additional_tags)

For documentation for python mode, check the rest of this documentation.

Python mode has the exactly same whitespace control as the standard mode does (the standard liquid template engine).

To enable python mode, you can either specify mode to python:
```python
from liquid import Liquid
Liquid(template, liquid_config={'mode': 'python'})
```
or use `LiquidPython`
```python
from liquid import LiquidPython
LiquidPython(template)
```

[1]: https://shopify.github.io/liquid/
