
!!! warning

    `Liquid.debug()` is deprecated, and takes no effect anymore. Use following instead:
    ```python
    liq = Liquid("...", liquid_loglevel='debug')
    ```

# Verbosity

There are three levels of verbosity `DEBUG`, `DETAIL` and `INFO (and above)`, based on the standard levels of `logging` mode. Here we define a `DETAIL` level with value of `15` to indicate the verbosity between `DEBUG` and `INFO`

Information shown at each level:

- `DEBUG`: shows everything, including the parsing process, filename and line number, and the compiled source code
- `DETAIL`: shows everything but the parsing process and compiled source code. This is the default level.
- `INFO`: shows only very basic information

Here is an example for information shown at each level:

```python
>>> from liquid import Liquid
>>> Liquid("{% python 1/0 %}", liquid_loglevel="debug").render()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/path/to/liquidpy/liquid/__init__.py", line 233, in render
    _render_failed(exc, finalcode, final_context)
  File "/path/to/liquidpy/liquid/__init__.py", line 118, in _render_failed
    raise LiquidRenderError('\n'.join(msg)) from None
liquid.exceptions.LiquidRenderError: [ZeroDivisionError] division by zero

Template call stacks:
--------------------------------------------------
File <LIQUID TEMPLATE SOURCE>
  > 1. {% python 1/0 %}

Compiled source (elevate loglevel to hide this)
--------------------------------------------------
  9.    # Environment and variables
  10.   true = _liquid_context['true']
  11.   false = _liquid_context['false']
  12.   nil = _liquid_context['nil']
  13.   _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']
> 14.   1/0
  15.
  16.   return ''.join(str(x) for x in _liquid_rendered)

Context:
--------------------------------------------------
  true: True
  false: False
  nil: None
```

```python
>>> Liquid("{% python 1/0 %}", liquid_loglevel="detail").render()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/paths/to/liquidpy/liquid/__init__.py", line 233, in render
    _render_failed(exc, finalcode, final_context)
  File "/paths/to/liquidpy/liquid/__init__.py", line 83, in _render_failed
    raise LiquidRenderError('\n'.join(msg)) from None
liquid.exceptions.LiquidRenderError: [ZeroDivisionError] division by zero

Template call stacks:
--------------------------------------------------
File <LIQUID TEMPLATE SOURCE>
  > 1. {% python 1/0 %}
```

```python
>>> Liquid("{% python 1/0 %}", liquid_loglevel="info").render()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/paths/to/liquidpy/liquid/__init__.py", line 233, in render
    _render_failed(exc, finalcode, final_context)
  File "/paths/to/liquidpy/liquid/__init__.py", line 71, in _render_failed
    raise LiquidRenderError(msg[0]) from None
liquid.exceptions.LiquidRenderError: [ZeroDivisionError] division by zero
```

# Template call stacks with include and extends

```python
>>> Liquid("{% extends tests/templates/parent4.liq %}", liquid_loglevel='debug').render()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  # ...
  # tracebacks
  # ...
liquid.exceptions.LiquidSyntaxError: 'for' node expects format: 'for var1, var2 in expr'

Template call stacks:
----------------------------------------------
File <LIQUID TEMPLATE SOURCE>
  > 1. {% extends tests/templates/parent4.liq %}
File /path/to/liquidpy/tests/templates/parent4.liq
  > 6. {% include include3.liq %}
File /path/to/liquidpy/tests/templates/include3.liq
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

# Parsing process

At `debug` level, we are able to see the parseing process, as well as the compiled source code. However, by default, there is no handler added to the logger. To see that, we need to add a handler:

```python
>>> import logging
>>> from liquid import Liquid, LOGGER
>>> LOGGER.addHandler(logging.StreamHandler())
>>> Liquid("{{1}}", liquid_loglevel="debug").render()
[PARSER 1] Initialized from <LIQUID TEMPLATE SOURCE>
[PARSER 1] - Found node '<liquid_expr>' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 1]   Parsing node '<liquid_expr>' at <LIQUID TEMPLATE SOURCE>:1
The compiled code:
def _liquid_render_function_47410234337432(_liquid_context):
  '''Main entrance function to render the template'''

  # Rendered content
  _liquid_rendered = []
  _liquid_ret_append = _liquid_rendered.append
  _liquid_ret_extend = _liquid_rendered.extend

  # Environment and variables
  true = _liquid_context['true']
  false = _liquid_context['false']
  nil = _liquid_context['nil']
  _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']

  # TAGGED CODE: _liquid_dodots_function

  def _liquid_dodots_function(obj, dot):
    '''Allow dot operation for a.b and a['b']'''
    try:
      return getattr(obj, dot)
    except (AttributeError, TypeError):
      return obj[dot]

  # ENDED TAGGED CODE

  _liquid_ret_append(1)

  return ''.join(str(x) for x in _liquid_rendered)

'1'
```

# Changing logger level while switch template by include or extends

You can change the logger level in different files to hide some parsing processes in different files:

```python
>>> Liquid("{% extends tests/templates/parent5.liq %}{{1}}", liquid_loglevel='debug').render()
[PARSER 1] Initialized from <LIQUID TEMPLATE SOURCE>
[PARSER 1] - Found node 'extends' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 1]   Parsing node 'extends' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 1] - Deferring node 'extends' at priority 999
[PARSER 1] - Found node '<liquid_expr>' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 1]   Parsing node '<liquid_expr>' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 1] - Parsing content of deferred(999) node 'extends' at <LIQUID TEMPLATE SOURCE>:1
[PARSER 2] Initialized from /path/to/liquidpy/tests/templates/parent5.liq
[PARSER 2] - Found node 'config' at /path/to/liquidpy/tests/templates/parent5.liq:1
[PARSER 2]   Parsing node 'config' at /path/to/liquidpy/tests/templates/parent5.liq:1
The compiled code:
def _liquid_render_function_47410234493080(_liquid_context):
  '''Main entrance function to render the template'''

  # Rendered content
  _liquid_rendered = []
  _liquid_ret_append = _liquid_rendered.append
  _liquid_ret_extend = _liquid_rendered.extend

  # Environment and variables
  true = _liquid_context['true']
  false = _liquid_context['false']
  nil = _liquid_context['nil']
  _liquid_liquid_filters = _liquid_context['_liquid_liquid_filters']

  # TAGGED CODE: _liquid_dodots_function

  def _liquid_dodots_function(obj, dot):
    '''Allow dot operation for a.b and a['b']'''
    try:
      return getattr(obj, dot)
    except (AttributeError, TypeError):
      return obj[dot]

  # ENDED TAGGED CODE

  _liquid_ret_append('empty block')

  # NODE CAPTURE: 47410234515640
  _liquid_capture_47410234515640 = []
  _liquid_ret_append = _liquid_capture_47410234515640.append
  _liquid_ret_extend = _liquid_capture_47410234515640.extend
  if (true):
    _liquid_ret_append('1')
  x = ''.join(str(_) for _ in _liquid_capture_47410234515640)
  del _liquid_capture_47410234515640
  _liquid_ret_append = _liquid_rendered.append
  _liquid_ret_extend = _liquid_rendered.extend
  # NODE CAPTURE END


  return ''.join(str(x) for x in _liquid_rendered)

'empty block'
```

!!! note

    Note that the parsing processes for `blocks` in `PARSER 2` is not showing as the loglevel is `info` in `parent5.liq`. Note that `{{1}}` parsing in `PARSER 1` is still showing, as changing loglevel in other template won't affect current parser.
