from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from liquid.liquid import Liquid
import pytest


def test_env_args(set_default_standard):
    loader = FileSystemLoader("~")
    tpl = Liquid(
        "{$ a $}",
        variable_start_string="{$",
        variable_end_string="$}",
        x=1,
        loader=loader,
    )
    assert tpl.render(a=1) == "1"
    assert tpl.env.x == 1


def test_from_env(set_default_standard):
    loader = FileSystemLoader("~")
    env = Environment(loader=loader)
    tpl = Liquid.from_env("{{ a }}", env)
    assert tpl.render(a=1) == "1"

def test_async_render(set_default_standard):
    import asyncio
    tpl = Liquid('{{ a }}', enable_async=True)

    try:
        run = asyncio.run
    except AttributeError:
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete

    assert run(tpl.render_async(a = 1)) == "1"
