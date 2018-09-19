from setuptools import setup, find_packages

# get version
from os import path
verfile = path.join(path.dirname(__file__), 'liquid', '__init__.py')
with open(verfile) as vf:
	VERSION = vf.readline().split('=')[1].strip()[1:-1]

setup (
	name             = 'liquidpy',
	version          = VERSION,
	description      = "A port of liquid template engine for python",
	url              = "https://github.com/pwwang/liquidpy",
	author           = "pwwang",
	author_email     = "pwwang@pwwang.com",
	license          = "Apache License Version 2.0",
	long_description = "https://github.com/pwwang/liquidpy",
	packages         = find_packages(),
	classifiers      = [
		"Intended Audience :: Developers",
		"Natural Language :: English",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
	]
)