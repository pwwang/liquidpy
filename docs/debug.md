
You may print debug information by setting `Liquid.DEBUG = True` globally to show the parsing and rendering processes. 
```python
Liquid.DEBUG = True
Liquid('{% python 1/0 %}').render()
```
```log
[2018-09-26 10:53:36,912 DEBUG] Mode: mixed debug
[2018-09-26 10:53:36,912 DEBUG] Token type: 'python', content: '1/0' at line 1: '{% python 1/0 %}'
[2018-09-26 10:53:36,912 DEBUG]  - parsing python literal: 1/0 
[2018-09-26 10:53:36,912 DEBUG] Python source:
[2018-09-26 10:53:36,912 DEBUG] --------------------------------------------------------------------------------
[2018-09-26 10:53:36,912 DEBUG] _liquid_rendered = []
[2018-09-26 10:53:36,912 DEBUG] _liquid_captured = []
[2018-09-26 10:53:36,912 DEBUG] _liquid_ret_append = _liquid_rendered.append
[2018-09-26 10:53:36,912 DEBUG] _liquid_ret_extend = _liquid_rendered.extend
[2018-09-26 10:53:36,912 DEBUG] _liquid_cap_append = _liquid_captured.append
[2018-09-26 10:53:36,912 DEBUG] _liquid_cap_extend = _liquid_captured.extend
[2018-09-26 10:53:36,912 DEBUG] 1/0
[2018-09-26 10:53:36,912 DEBUG] _liquid_rendered_str = ''.join(str(x) for x in _liquid_rendered)
[2018-09-26 10:53:36,912 DEBUG] del _liquid_captured
[2018-09-26 10:53:36,913 DEBUG] del _liquid_cap_append
[2018-09-26 10:53:36,913 DEBUG] del _liquid_cap_extend
[2018-09-26 10:53:36,913 DEBUG] del _liquid_filters
[2018-09-26 10:53:36,913 DEBUG] del _liquid_rendered
[2018-09-26 10:53:36,913 DEBUG] del _liquid_ret_append
[2018-09-26 10:53:36,913 DEBUG] del _liquid_ret_extend
# raise LiquidRenderError: ZeroDivisionError: integer division or modulo by zero, at line 1: {% python 1/0 %}
```

You may turn `DEBUG` mode on/off for single `Liquid` instance by just putting `debug` or `nodebug` in the FIRST LINE of your template:
```liquid
{% mode compact, nodebug %}
{% python 1/0 %}
# no debug information will be shown
# raise LiquidRenderError: ZeroDivisionError: integer division or modulo by zero, at line 1: {% python 1/0 %}
```
