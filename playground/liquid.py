from pyweb import pydom
from liquid import Liquid

EXAMPLE_TEMPLATE = "{{ a | upper }}"
EXAMPLE_VARIABLES = "a = 'hello world!'"
EXAMPLE_FILTERS = """\
def upper(value):
    return value.upper()
"""

TEMPLATE_CONTAINER = pydom["#template"][0]
VARIABLES_CONTAINER = pydom["#variables"][0]
FILTERS_CONTAINER = pydom["#filters"][0]
MODE_CONTAINER = pydom["#mode"][0]
RENDERED_CONTAINER = pydom["#rendered"][0]


def _remove_class(element, class_name):
    try:
        element.classes.remove(class_name)
    except ValueError:
        pass


def _add_class(element, class_name):
    element.classes.append(class_name)


def _error(message):
    """
    Displays an error message.
    """
    _add_class(RENDERED_CONTAINER, "bg-red-100")
    RENDERED_CONTAINER.value = message


def load_example(*args, **kwargs):
    """
    Loads the example template, variables and filters.
    """
    TEMPLATE_CONTAINER.value = EXAMPLE_TEMPLATE
    VARIABLES_CONTAINER.value = EXAMPLE_VARIABLES
    FILTERS_CONTAINER.value = EXAMPLE_FILTERS


def render(*args, **kwargs):
    """
    Renders the template with the variables and filters.
    """
    template = TEMPLATE_CONTAINER.value
    variables = {}
    try:
        exec(VARIABLES_CONTAINER.value, variables)
    except Exception as e:
        _error(f"Something wrong when evaluating variables: \n{e}")
        return

    filters = {}
    try:
        exec(FILTERS_CONTAINER.value, filters)
    except Exception as e:
        _error(f"Something wrong when evaluating filters: \n{e}")
        return

    mode = MODE_CONTAINER.value
    _remove_class(RENDERED_CONTAINER, "bg-red-100")
    try:
        liq = Liquid(template, from_file=False, mode=mode, filters=filters)
        RENDERED_CONTAINER.value = liq.render(**variables)
    except Exception as e:
        _error(f"Something wrong when rendering: \n{e}")
