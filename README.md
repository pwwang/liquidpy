# liquidpy
A port of [liquid][1] template engine for python

[![Pypi][2]][9] [![Github][3]][10] [![PythonVers][4]][9] [![ReadTheDocs building][13]][8] [![Travis building][5]][11] [![Codacy][6]][12] [![Codacy coverage][7]][12]

## Install
```shell
pip install liquidpy
```

## Current status and plans
- Note that this branch is not fully compatible with shopify's liquid. For compatible versions, please check branches [lark][14] and [larkone][15].
- This branch is current NOT safe agaist malicious input ([#22][16]), so we tried to re-implement the engine using `lark-parser`. However, both versions were very slow for lexer.
- With branch `lark`, we tried to tokenize each tag and parse the content of the tags later using independent parsers, while with `larkone`, we tried to put all grammars together, and made it into a universal parser. However, both of them are slow, due to tokenization of whole tags (`raw` and `comment`) and literals (See `grammar.lark` in the code).
- If you have a better grammar or idea for tokenization, you are very welcome to submit issues or PRs (writing naive lexer is just too much work).
- We left some APIs to extend the `lark` ones with some functions from `master`. However, it won't happen before we find a faster lexer.
- A temporary plan for the `master` branch is to do some security check to address [#22][16].

## Full Documentation
[ReadTheDocs][8]

## Baisic usage
```python
from liquid import Liquid
liq = Liquid('{{a}}')
ret = liq.render(a = 1)
# ret == '1'

# load template from a file
liq = Liquid('/path/to/template', liquid_from_file=True)
```
With environments:
```python
liq = Liquid('{{a | os.path.basename}}', os=__import__('os'))
ret = liq.render(a="path/to/file.txt")
# ret == 'file.txt'
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
[14]: https://github.com/pwwang/liquidpy/tree/lark
[15]: https://github.com/pwwang/liquidpy/tree/larkone
[16]: https://github.com/pwwang/liquidpy/issues/22
