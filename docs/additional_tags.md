## Tag block

A block tag is to define a block for a parent template as a placeholder or a block in a inherited template to replace the corresponding one in the parent template.

The tags in a block will not be parsed immediately until it's been replaced by the one from child template or replaces the one from parent template.

To define a block tag:
```liquid
{% block blockname %}
...
{% endblock %}
```

## Tag include

You can also include a sub-template in a template. The syntax is similar to the one from Jekyll:
```liquid
{% include <path/to/sub-template.liquid> arg1=value1 arg2=value2 ... %}
```

We don't support variables for the path of the sub-template. So here you have to pass the path directly. It can be either quoted or not. If you have spaces in the path, you need to quote it.

Like Jekyll's include tag, you can also templatize the content and use each variables passed in a parameters:
```liquid
The arg1 is {{include.arg1}}
The arg2 is {{include.arg2}}
```

## Tag extends

The extends tag is used to extend a sub-template from a parent one by replacing the content wrapped with the block tag with the ones in the parent.

The full syntax is like:

`parent.liquid`:
```liquid
<html>
    <head>
        {% block title %}Default title{% endblock %}
    </head>
    <body>
        {% block body %}
        {% endblock %}
    </body>
</html>
```

`sub.liquid`
```liquid
{% extends parent.liquid %}

{% block title %}
Title of the sub-template
{% endblock %}

{% block body %}
Awesome body content of the sub-template
{% endblock %}
```

Then the template will be compiled as:
```liquid
<html>
    <head>
        {% block title %}
        Title of the sub-template
        {% endblock %}
    </head>
    <body>
        {% block body %}
        Awesome body content of the sub-template
        {% endblock %}
    </body>
</html>
```

!!! Note

    About the paths of `include` and `extends`:

    We support both relative and absolute paths for those two tags. For the relative ones, `liquidpy` will look for the template in the directory specifiied by `Liquid(..., liquid_config={'include_dir': [...]}` and `Liquid(..., liquid_config={'extends_dir': [...]}`, respectively. If nothing found there, it will look for the template in the directory where the one cites them.

    If the template citing them is from a string, it will search in the current working directory (`./`, the directory the main program is running from)

    One can also specify `include_dir` and `extends_dir` by `config` tag when `strict` is off while constructing the Liquid object:
    ```python
    Liquid(..., liquid_config={'strict': False})
    ```

    `strict` is True by default.

    See [Configuration](../configuration) for more details.


## Tag config

See [Configuration](../configuration)
