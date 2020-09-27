import pytest
from pathlib import Path
from liquid import *

def test_config_error():
    Liquid('{% config debug%}', {'strict': False})

    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid("{% config no_such_item %}")

    assert 'Tag not allowed in strict mode' in str(exc.value)

    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config no_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config strict=true %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config \nno_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config cache=false\nno_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config cache=true\n\ninclude_dir='noadir' %}",
               {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config cache=true include_dir='noadir' %}",
               {'strict': False})

