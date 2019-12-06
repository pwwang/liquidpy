
liquidpy
========

A port of `liquid <https://shopify.github.io/liquid/>`_ template engine for python

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
.. image:: https://img.shields.io/readthedocs/liquidpy?style=flat-square
   :target: https://img.shields.io/readthedocs/liquidpy?style=flat-square
   :alt: ReadTheDocs building
 <https://liquidpy.readthedocs.io/en/latest/>`_ `
.. image:: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
   :target: https://img.shields.io/travis/pwwang/liquidpy.svg?style=flat-square
   :alt: Travis building
 <https://travis-ci.org/pwwang/liquidpy>`_ `
.. image:: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy
 <https://app.codacy.com/manual/pwwang/liquidpy/dashboard>`_ `
.. image:: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy coverage
 <https://app.codacy.com/manual/pwwang/liquidpy/dashboard>`_

Install
-------

.. code-block:: shell

   pip install liquidpy

Full Documentation
------------------

`ReadTheDocs <https://liquidpy.readthedocs.io/en/latest/>`_

Baisic usage
------------

.. code-block:: python

   from liquid import Liquid
   liq = Liquid('{{a}}')
   ret = liq.render(a = 1)
   # ret == '1'

With environments:

.. code-block:: python

   liq = Liquid('{{a | os.path.basename}}', os = __import__('os'))
   ret = liq.render(a = "path/to/file.txt")
   # ret == 'file.txt'
