
liquidpy
========

A port of `liquid <https://shopify.github.io/liquid/>`_ template engine for python on the shoulders of `jinja2 <https://jinja.palletsprojects.com/>`_

`
.. image:: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
   :target: https://img.shields.io/pypi/v/liquidpy.svg?style=flat-square
   :alt: Pypi
 <https://pypi.org/project/liquidpy/>`_ `
.. image:: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
   :target: https://img.shields.io/github/tag/pwwang/liquidpy.svg?style=flat-square
   :alt: Github
 <https://github.com/pwwang/liquidpy>`_ `
.. image:: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
   :target: https://img.shields.io/pypi/pyversions/liquidpy.svg?style=flat-square
   :alt: PythonVers
 <https://pypi.org/project/liquidpy/>`_ `
.. image:: https://img.shields.io/github/workflow/status/pwwang/liquidpy/docs?style=flat-square
   :target: https://img.shields.io/github/workflow/status/pwwang/liquidpy/docs?style=flat-square
   :alt: Docs building
 <https://github.com/pwwang/liquidpy/actions>`_ `
.. image:: https://img.shields.io/github/workflow/status/pwwang/liquidpy/building?style=flat-square
   :target: https://img.shields.io/github/workflow/status/pwwang/liquidpy/building?style=flat-square
   :alt: Travis building
 <https://github.com/pwwang/liquidpy/actions>`_ `
.. image:: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy
 <https://app.codacy.com/gh/pwwang/liquidpy/dashboard>`_ `
.. image:: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy coverage
 <https://app.codacy.com/gh/pwwang/liquidpy/dashboard>`_

Install
-------

.. code-block:: shell

   pip install -U liquidpy

Baisic usage
------------

Loading a template
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from liquid import Liquid
   liq = Liquid('{{a}}', from_file=False)
   ret = liq.render(a = 1)
   # ret == '1'

   # load template from a file
   liq = Liquid('/path/to/template.html')

Using jinja's environment

.. code-block:: python

   from jinja2 import Environment, FileSystemLoader
   env = Environment(loader=FileSystemLoader('./'), ...)

   liq = Liquid.from_env("/path/to/template.html", env)

Switching to a different mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

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

Changing default options
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from liquid import defaults, Liquid
   defaults.FROM_FILE = False
   defaults.MODE = 'wild'

   # no need to pass from_file and mode anymore
   liq = Liquid('{% from_ os import path %}{{path.basename("a/b.txt")}}')
   liq.render()
   # 'b.txt'

Documentation
-------------


* `Liquidpy's documentation <https://pwwang.github.io/liquidpy>`_
* `Liquid documentation (standard) <https://shopify.github.io/liquid/>`_
* `Liquid documentation (jekyll) <https://jekyllrb.com/docs/liquid/>`_
* `Liquid documentation (shopify-extended) <https://shopify.dev/api/liquid>`_
