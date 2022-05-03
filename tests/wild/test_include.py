from liquid import Liquid
from pathlib import Path

def test_include(set_default_wild):
    subtpl = Path(__file__).parent.joinpath("subtpl.liq")

    # default
    tpl = f"""
    {{% assign variable = 8525 %}}
    {{% include "{subtpl}" %}}
    """
    out = Liquid(tpl).render().strip()
    assert out == "|8525|"

    # with context
    tpl = f"""
    {{% assign variable = 8525 %}}
    {{% include "{subtpl}" with context %}}
    """
    out = Liquid(tpl).render().strip()
    assert out == "|8525|"

    # without context
    tpl = f"""
    {{% assign variable = 8525 %}}
    {{% include "{subtpl}" without context %}}
    """
    out = Liquid(tpl).render().strip()
    assert out == "||"
