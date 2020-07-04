"""This enables loading all tags from inside this directory

by `from . import tags`
"""

import pkgutil

for _, tagmod, _ in pkgutil.walk_packages(__path__, prefix=__name__ + '.'):
    __import__(tagmod)
