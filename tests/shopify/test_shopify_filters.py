import pytest  # noqa: F401
from liquid import Liquid


def test_filter(set_default_shopify):
    assert Liquid('').render() == ''
