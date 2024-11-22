from liquid import Liquid

EXAMPLE_TEMPLATE = "{{ a | upper }}"
EXAMPLE_VARIABLES = "a = 'hello world!'"
EXAMPLE_FILTERS = """\
def upper(value):
    return value.upper()
"""

TEMPLATE_CONTAINER = Element("template")
VARIABLES_CONTAINER = Element("variables")
FILTERS_CONTAINER = Element("filters")
MODE_CONTAINER = Element("mode")
RENDERED_CONTAINER = Element("rendered")

def _remove_class(element, class_name):
    element.element.classList.remove(class_name)


def _add_class(element, class_name):
    element.element.classList.add(class_name)


def _error(message):
    """
    Displays an error message.
    """
    _add_class(RENDERED_CONTAINER, "bg-red-100")
    RENDERED_CONTAINER.element.value = message


def load_example(*args, **kwargs):
    """
    Loads the example template, variables and filters.
    """
    TEMPLATE_CONTAINER.element.value = EXAMPLE_TEMPLATE
    VARIABLES_CONTAINER.element.value = EXAMPLE_VARIABLES
    FILTERS_CONTAINER.element.value = EXAMPLE_FILTERS


def render(*args, **kwargs):
    """
    Renders the template with the variables and filters.
    """
    template = TEMPLATE_CONTAINER.element.value
    variables = {}
    try:
        exec(VARIABLES_CONTAINER.element.value, variables)
    except Exception as e:
        _error(f"Something wrong when evaluating variables: \n{e}")
        return

    filters = {}
    try:
        exec(FILTERS_CONTAINER.element.value, filters)
    except Exception as e:
        _error(f"Something wrong when evaluating filters: \n{e}")
        return

    mode = MODE_CONTAINER.element.value
    _remove_class(RENDERED_CONTAINER, "bg-red-100")
    try:
        liq = Liquid(template, from_file=False, mode=mode, filters=filters)
        RENDERED_CONTAINER.element.value = liq.render(**variables)
    except Exception as e:
        _error(f"Something wrong when rendering: \n{e}")
