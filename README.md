# liquidpy
A port of [liquid][1] template engine for python on the shoulders of [jinja2][17]

[![Pypi][2]][9] [![Github][3]][10] [![PythonVers][4]][9] [![ReadTheDocs building][13]][8] [![Travis building][5]][11] [![Codacy][6]][12] [![Codacy coverage][7]][12]

## Install
```shell
pip install liquidpy
```

## Baisic usage

### Load a template
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

### Switch to a different mode

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

### Change default options

```python
from liquid import defaults, Liquid
defaults.FROM_FILE = False
defaults.MODE = 'wild'

# no need to pass from_file and mode anymore
liq = Liquid('{% from_ os import path %}{{path.basename("a/b.txt")}}')
liq.render()
# 'b.txt'
```


## Full Documentation
[https://pwwang.github.io/liquidpy][8]


[1]: https://shopify.github.io/liquid/
[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
[5]: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
[6]: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[7]: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[8]: https://pwwang.github.io/liquidpy
[9]: https://pypi.org/project/liquidpy/
[10]: https://github.com/pwwang/liquidpy
[11]: https://travis-ci.org/pwwang/liquidpy
[12]: https://app.codacy.com/manual/pwwang/liquidpy/dashboard
[13]: https://img.shields.io/readthedocs/liquidpy?style=flat-square
[14]: https://github.com/pwwang/liquidpy/tree/lark
[15]: https://github.com/pwwang/liquidpy/tree/larkone
[16]: https://github.com/pwwang/liquidpy/issues/22
[17]: https://jinja.palletsprojects.com/
