# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['liquid', 'liquid.exts', 'liquid.filters', 'liquid.tags']

package_data = \
{'': ['*']}

install_requires = \
['jinja2>=3,<4']

setup_kwargs = {
    # 'name': 'liquidpy',
    'version': '0.7.0',
    'description': 'A port of liquid template engine for python',
    'long_description': '# liquidpy\nA port of [liquid][19] template engine for python, on the shoulder of [jinja2][17]\n\n[![Pypi][2]][9] [![Github][3]][10] [![PythonVers][4]][9] [![Docs building][13]][11] [![Travis building][5]][11] [![Codacy][6]][12] [![Codacy coverage][7]][12]\n\n## Install\n```shell\npip install -U liquidpy\n```\n\n## Baisic usage\n\n### Loading a template\n```python\nfrom liquid import Liquid\nliq = Liquid(\'{{a}}\', from_file=False)\nret = liq.render(a = 1)\n# ret == \'1\'\n\n# load template from a file\nliq = Liquid(\'/path/to/template.html\')\n```\n\nUsing jinja\'s environment\n```python\nfrom jinja2 import Environment, FileSystemLoader\nenv = Environment(loader=FileSystemLoader(\'./\'), ...)\n\nliq = Liquid.from_env("/path/to/template.html", env)\n```\n\n### Switching to a different mode\n\n```python\nliq = Liquid(\n    """\n    {% python %}\n    from os import path\n    filename = path.join("a", "b")\n    {% endpython %}\n    {{filename}}\n    """,\n    mode="wild" # supported: standard(default), jekyll, shopify, wild\n)\nliq.render()\n# \'a/b\'\n```\n\n### Changing default options\n\n```python\nfrom liquid import defaults, Liquid\ndefaults.FROM_FILE = False\ndefaults.MODE = \'wild\'\n\n# no need to pass from_file and mode anymore\nliq = Liquid(\'{% from_ os import path %}{{path.basename("a/b.txt")}}\')\nliq.render()\n# \'b.txt\'\n```\n\n\n## Documentation\n\n- [Liquidpy\'s documentation][8]\n- [Liquid documentation (standard)][19]\n- [Liquid documentation (jekyll)][18]\n- [Liquid documentation (shopify-extended)][1]\n- [Jinja2\'s documentation][20]\n\n\n[1]: https://shopify.dev/api/liquid\n[2]: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square\n[3]: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square\n[4]: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square\n[5]: https://img.shields.io/github/workflow/status/pwwang/liquidpy/building?style=flat-square\n[6]: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square\n[7]: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square\n[8]: https://pwwang.github.io/liquidpy\n[9]: https://pypi.org/project/liquidpy/\n[10]: https://github.com/pwwang/liquidpy\n[11]: https://github.com/pwwang/liquidpy/actions\n[12]: https://app.codacy.com/gh/pwwang/liquidpy/dashboard\n[13]: https://img.shields.io/github/workflow/status/pwwang/liquidpy/docs?style=flat-square\n[14]: https://github.com/pwwang/liquidpy/tree/lark\n[15]: https://github.com/pwwang/liquidpy/tree/larkone\n[16]: https://github.com/pwwang/liquidpy/issues/22\n[17]: https://jinja.palletsprojects.com/\n[18]: https://jekyllrb.com/docs/liquid/\n[19]: https://shopify.github.io/liquid/\n[20]: https://jinja.palletsprojects.com/\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/liquidpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(name='liquidpy', **setup_kwargs)
