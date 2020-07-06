# liquidpy
A port of [liquid][1] template engine for python

This is the branch with compatibility to shopify's liquid template language.

[![Pypi][2]][9] [![Github][3]][10] [![PythonVers][4]][9] [![ReadTheDocs building][13]][8] [![Travis building][5]][11] [![Codacy][6]][12] [![Codacy coverage][7]][12]

## Install
```shell
pip install git+https://github.com/pwwang/liquidpy@lark
# or
pip install git+https://github.com/pwwang/liquidpy@larkone
```

## Full Documentation
Check shopify's liquid [documentation][1]

## Baisic usage
```python
from liquid import Liquid
liq = Liquid('{{a}}')
ret = liq.render(a=1)
# ret == '1'

# with environments pre-loaded
liq = Liquid('{{a}}', a=1)
ret = liq.render()
# ret == '1'

# With debug on:
liq = Liquid('{{a}}', liquid_config={'debug': True})
# or with more verbosed message
liq = Liquid('{{a}}', liquid_config={'debug': 'plus'})
```

[1]: https://shopify.github.io/liquid/
[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
[5]: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
[6]: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[7]: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
[8]: https://liquidpy.readthedocs.io/en/latest/
[9]: https://pypi.org/project/liquidpy/
[10]: https://github.com/pwwang/liquidpy
[11]: https://travis-ci.org/pwwang/liquidpy
[12]: https://app.codacy.com/manual/pwwang/liquidpy/dashboard
[13]: https://img.shields.io/readthedocs/liquidpy?style=flat-square
