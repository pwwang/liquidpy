
You may print debug information by setting `Liquid.debug(True)` globally to show the parsing and rendering processes.
```python
Liquid.debug(True)
Liquid('{% python 1/0 %}').render()
```
```python
[2019-10-29 00:36:40,592 DEBUG] Literals wrapped by tags [None, '{%'] found at line 1: ''
[2019-10-29 00:36:40,592 DEBUG] Statement found at line 1: {% python 1/0 %}
[2019-10-29 00:36:40,592 DEBUG] Literals wrapped by tags ['%}', None] found at line 1: ''
[2019-10-29 00:36:40,592 DEBUG] The compiled code:
def _liquid_render_function(_liquid_context):
  true = _liquid_context['true']
  false = _liquid_context['false']
  nil = _liquid_context['nil']
  _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']
  _liquid_rendered = []
  _liquid_ret_append = _liquid_rendered.append
  _liquid_ret_extend = _liquid_rendered.extend
  1/0
  return ''.join(str(x) for x in _liquid_rendered)

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/.../liquidpy/liquid/__init__.py", line 162, in render
    raise LiquidRenderError('\n'.join(msg))
liquid.exceptions.LiquidRenderError: ZeroDivisionError: division by zero

At source line 1:
----------------------------------------------
> 1. {% python 1/0 %}

Compiled source (turn debug off to hide this):
----------------------------------------------
  4.    nil = _liquid_context['nil']
  5.    _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']
  6.    _liquid_rendered = []
  7.    _liquid_ret_append = _liquid_rendered.append
  8.    _liquid_ret_extend = _liquid_rendered.extend
> 9.    1/0
  10.   return ''.join(str(x) for x in _liquid_rendered)

Context:
----------------------------------------------

```

You may turn `DEBUG` mode on/off for single `Liquid` instance by just putting `debug` or `info` in the `{% mode ... %}` block:
```liquid
{% mode compact info %}
{% python 1/0 %}
# no detailed debug information will be shown
```
```python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/.../liquidpy/liquid/__init__.py", line 148, in render
    raise LiquidRenderError('\n'.join(msg))
liquid.exceptions.LiquidRenderError: ZeroDivisionError: division by zero

At source line 1:
----------------------------------------------
> 1. {% python 1/0 %}

```


If you have inclusions and inheritance with the template, we will show a call stacks for those templates.

```python
liquid.exceptions.LiquidSyntaxError: Statement "for" expects format: "for var1, var2 in expr"

Template call stacks:
----------------------------------------------
File <LIQUID TEMPLATE SOURCE>
  > 1. {% extends /.../liquidpy/tests/templates/parent4.liq %}
File /.../liquidpy/tests/templates/parent4.liq
  > 6. {% include include3.liq %}
File /.../liquidpy/tests/templates/include3.liq
    4.  4. comment
    5.  5. {% endcomment %}
    6.  6. {% for multi
    7.  7.    line, just
    8.  8.    to check if the
  > 9.  9.    line number is correct %}
    10. 10. {{ "I have" +
    11. 11.  "some other lines" }}
    12. 12. {% endfor %}
```
