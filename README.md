# liquidpy
A port of [liquid][1] template engine for python

![Pypi][2] ![Github][3] ![PythonVers][4] ![Travis building][5]  ![Codacy][6] ![Codacy coverage][7]

## Install
```shell
# install released version
pip install liquidpy
# install lastest version
pip install git+https://github.com/pwwang/liquidpy.git
```

## Full Documentation
[ReadTheDocs][8]

## Baisic usage
```python
from liquid import Liquid
liq = Liquid('{{a}}')
ret = liq.render(a = 1)
# ret == '1'
```
With environments:
```python
liq = Liquid('{{os.path.basename(a)}}', os = __import__('os'))
ret = liq.render(a = "path/to/file.txt")
# ret == 'file.txt'
```

[1]: https://shopify.github.io/liquid/
[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
[5]: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
[6]: https://api.codacy.com/project/badge/Grade/ddbe1b0441f343f5abfdec3811a4e482
[7]: https://api.codacy.com/project/badge/Coverage/ddbe1b0441f343f5abfdec3811a4e482
[8]: https://liquidpy.readthedocs.io/en/latest/
