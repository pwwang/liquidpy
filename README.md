# pyliquid
A port of liquid template engine for python  
See liquid: https://shopify.github.io/liquid/

## Install

## Baisic usage
```python
from liquid import Liquid
liq = Liquid('{{a}}')
ret = liq.render({'a': 1})
# ret == '1'
```
With environments:
```python
liq = Liquid('{{os.path.basename(a)}}', {'os': __import__('os')})
ret = liq.render({'a': "path/to/file.txt"})
# ret == 'file.txt'
```

## Liquid features
### White space control
**Input**
```liquid
{% assign my_variable = "tomato" %}
{{ my_variable }}
```
**Output**
```

tomato
```

## `pyliquid` specific features
### Global white space control
