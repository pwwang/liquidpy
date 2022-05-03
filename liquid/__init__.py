"""A port of liquid template engine for python on the shoulders of jinja2"""
from .liquid import Liquid
from .patching import patch_jinja, unpatch_jinja

patch_jinja()

__version__ = "0.7.4"
