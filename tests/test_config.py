from pathlib import Path
import logging
import pytest

from liquid.config import LiquidConfig
from liquid.defaults import LIQUID_LOGGER_NAME

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def test_init():
    config = LiquidConfig(mode='compact', loglevel='debug', include='./',
                          extends=None)
    assert isinstance(config, LiquidConfig)
    assert config.mode == 'compact'
    assert config.loglevel == 10
    assert config.include == [Path('./').resolve()]
    assert config.extends == []

def test_extends():
    config = LiquidConfig(mode='compact', loglevel='debug', include='./',
                          extends=None)
    config.extends = __file__, ''
    assert config.extends == [Path(__file__).resolve()]

def test_tear():
    config = LiquidConfig(mode='compact', loglevel='debug', include='./',
                          extends=None)
    assert LOGGER.level == 10
    with config.tear() as conf:
        conf.loglevel = 'info'
        assert LOGGER.level == 20
    assert LOGGER.level == 10

def test_rest():
    config = LiquidConfig(mode='compact', loglevel='debug', include='./',
                          extends=None)
    config.include = 'templates', __file__
    assert Path(__file__).parent.resolve().joinpath('templates') in config.include
    assert len(config.include) == 2

    config = LiquidConfig(mode='compact', loglevel='debug', include='./',
                          extends=None)
    config.include = str(Path(__file__).parent.resolve().joinpath('templates')), ''
    assert Path(__file__).parent.resolve().joinpath('templates') in config.include
    assert len(config.include) == 2

    config.extends = 'templates', __file__
    assert Path(__file__).parent.resolve().joinpath('templates') in config.extends
    assert len(config.extends) == 1

    with pytest.raises(ValueError):
        config.mode = 'nosuchmode'