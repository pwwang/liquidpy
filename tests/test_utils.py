import pytest
from liquid.utils import *

def test_nothing():
    assert repr(NOTHING) == 'NOTHING'

def test_singleton():
    from liquid.tags.manager import TagManager, tag_manager
    assert TagManager() is tag_manager

def test_check_name():
    with pytest.raises(LiquidNameError):
        check_name(['__LIQUID_FILTERS__'])

def test_shorten():
    assert shorten('abcdefg', 6) == 'ab ...'
