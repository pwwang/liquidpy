
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
.. image:: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/grade/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy
 <https://app.codacy.com/manual/pwwang/liquidpy/dashboard>`_ `
.. image:: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :target: https://img.shields.io/codacy/coverage/aed04c099cbe42dabda2b42bae557fa4?style=flat-square
   :alt: Codacy coverage
 <https://app.codacy.com/manual/pwwang/liquidpy/dashboard>`_ 
.. image:: https://img.shields.io/github/workflow/status/pwwang/liquidpy/Build%20Docs?label=docs&style=flat-square
   :target: https://img.shields.io/github/workflow/status/pwwang/liquidpy/Build%20Docs?label=docs&style=flat-square
   :alt: Docs building
 
.. image:: https://img.shields.io/github/workflow/status/pwwang/liquidpy/Build%20and%20Deploy?style=flat-square
   :target: https://img.shields.io/github/workflow/status/pwwang/liquidpy/Build%20and%20Deploy?style=flat-square
   :alt: Building


This is compatible with `standard Liquid <https://shopify.github.io/liquid/>`_ template engine. Variations, such as Shopify and Jekyll are not fully supported yet.

Install
-------

.. code-block:: shell

   pip install -U liquidpy

Baisic usage
------------

.. code-block:: python

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

Python mode
-----------

We also support a python mode template engine, which acts more pythonic and powerful.

.. code-block:: python

   from liquid import Liquid
   # standard liquid doesn't support this
   liq = Liquid('{{a + 1}}', {'mode': 'python'})
   ret = liq.render(a=1)
   # ret == '2'

Both modes can accept a path, a file-like object or a stream for the template:

.. code-block:: python

   Liquid('/path/to/template')
   # or
   with open('/path/to/template') as f:
       Liquid(f)

Full Documentation
------------------


* Liquid's `documentation <https://shopify.github.io/liquid/>`_
* Liquidpy's `documentation <https://pwwang.github.io/liquidpy/>`_

Backward compatiblility warning
-------------------------------

``v0.6.0+`` is a remodeled version to make it compatible with standard liquid engine. If you are using a previous version, stick with it. ``0.6.0+`` is not fully compatible with previous versions.
