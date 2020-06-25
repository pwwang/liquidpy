import pkgutil

for _, tagmod, _ in pkgutil.walk_packages(__path__, prefix=__name__ + '.'):
    __import__(tagmod)
