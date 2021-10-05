import pytest
from pathlib import Path
from liquid import Liquid

TPLDIR = Path(__file__).parent / "templates"


def test_include_relative(set_default_jekyll):
    liq = Liquid(TPLDIR / "parent.tpl", from_file=True)
    assert liq.render().strip() == "sub"

    liq = Liquid(
        f'{{% include_relative "{TPLDIR}/parent.tpl" %}}',
    )
    assert liq.render().strip() == "sub"
