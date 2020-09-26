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


## Tag config

See [Configuration](../configuration)
