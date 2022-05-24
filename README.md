# liquidpy
A port of [liquid][19] template engine for python, on the shoulder of [jinja2][17]

[![Pypi][2]][9] [![Github][3]][10] [![PythonVers][4]][9] [![Docs building][13]][11] [![Travis building][5]][11] [![Codacy][6]][12] [![Codacy coverage][7]][12]

## Install
```shell
pip install -U liquidpy
```

## Playground

Powered by [pyscript][21]:

[https://pwwang.github.io/liquidpy/playground][22]

## Baisic usage

### Loading a template
```python
from liquid import Liquid
liq = Liquid('{{a}}', from_file=False)
ret = liq.render(a = 1)
# ret == '1'

# load template from a file
liq = Liquid('/path/to/template.html')
```

Using jinja's environment
```python
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./'), ...)

liq = Liquid.from_env("/path/to/template.html", env)
```

### Switching to a different mode

```python
liq = Liquid(
    """
    {% python %}
    from os import path
    filename = path.join("a", "b")
    {% endpython %}
    {{filename}}
    """,
    mode="wild" # supported: standard(default), jekyll, shopify, wild
)
liq.render()
# 'a/b'
```

### Changing default options

```python
from liquid import defaults, Liquid
defaults.FROM_FILE = False
defaults.MODE = 'wild'

# no need to pass from_file and mode anymore
liq = Liquid('{% from_ os import path %}{{path.basename("a/b.txt")}}')
liq.render()
# 'b.txt'
```


## Documentation

- [Liquidpy's documentation][8]
- [Liquid documentation (standard)][19]
- [Liquid documentation (jekyll)][18]
- [Liquid documentation (shopify-extended)][1]
- [Jinja2's documentation][20]


[1]: https://shopify.dev/api/liquid
[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
[5]: https://img.shields.io/github/workflow/status/pwwang/liquidpy/building?style=flat-square
[6]: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[7]: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[8]: https://pwwang.github.io/liquidpy
[9]: https://pypi.org/project/liquidpy/
[10]: https://github.com/pwwang/liquidpy
[11]: https://github.com/pwwang/liquidpy/actions
[12]: https://app.codacy.com/gh/pwwang/liquidpy/dashboard
[13]: https://img.shields.io/github/workflow/status/pwwang/liquidpy/docs?style=flat-square
[14]: https://github.com/pwwang/liquidpy/tree/lark
[15]: https://github.com/pwwang/liquidpy/tree/larkone
[16]: https://github.com/pwwang/liquidpy/issues/22
[17]: https://jinja.palletsprojects.com/
[18]: https://jekyllrb.com/docs/liquid/
[19]: https://shopify.github.io/liquid/
[20]: https://jinja.palletsprojects.com/
[21]: https://pyscript.net/
[22]: https://pwwang.github.io/liquidpy/playground
