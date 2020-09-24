import pytest
from pathlib import Path
from liquid import *

def test_config_error():
    Liquid('{% config debug strict=false %}', {'strict': False})

    with pytest.raises(LiquidSyntaxError) as exc:
        Liquid("{% config no_such_item %}")

    assert 'Tag not allowed in strict mode' in str(exc.value)

    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config no_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config \nno_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config strict=false\nno_such_item %}", {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config strict=false\n\ninclude_dir='noadir' %}",
               {'strict': False})
    with pytest.raises(LiquidRenderError) as exc:
        Liquid("{% config strict=false include_dir='noadir' %}",
               {'strict': False})

