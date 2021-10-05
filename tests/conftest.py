import pytest
from liquid import defaults

@pytest.fixture
def set_default_standard():
    orig_mode = defaults.MODE
    orig_from_file = defaults.FROM_FILE
    defaults.MODE = "standard"
    defaults.FROM_FILE = False
    yield
    defaults.MODE = orig_mode
    defaults.FROM_FILE = orig_from_file

@pytest.fixture
def set_default_wild():
    orig_mode = defaults.MODE
    orig_from_file = defaults.FROM_FILE
    defaults.MODE = "wild"
    defaults.FROM_FILE = False
    yield
    defaults.MODE = orig_mode
    defaults.FROM_FILE = orig_from_file

@pytest.fixture
def set_default_jekyll():
    orig_mode = defaults.MODE
    orig_from_file = defaults.FROM_FILE
    defaults.MODE = "jekyll"
    defaults.FROM_FILE = False
    yield
    defaults.MODE = orig_mode
    defaults.FROM_FILE = orig_from_file

@pytest.fixture
def set_default_shopify():
    orig_mode = defaults.MODE
    orig_from_file = defaults.FROM_FILE
    defaults.MODE = "shopify"
    defaults.FROM_FILE = False
    yield
    defaults.MODE = orig_mode
    defaults.FROM_FILE = orig_from_file
