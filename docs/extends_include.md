# Template inclusion and inheritance

## Inclusion
You can put {% include ... %} somewhere in your template to include the content of another template.

It can be even put in a statement block. For example:
```liquid
The calculated X value is:
{% include calculate_x.liquid %}
{{x}}
```

`calculate_x.liquid`
```liquid
{% assign x = x * 10 %}
```

```python
# without the include statement
# liquid.render(x = 1) == '1'
# but with it:
liquid.render(x = 1) == '10'
```

!!! hint

	- You can also use `{% include ... %}` inside a template to be included
	- You can, but don't have to use quote for the included file path

## Inheritance

A template can be inherited from a parent template. You just need to put `{% extends ... %}` at the top of the template or at the second place while the first is `{% mode ... %}`

The parent template should have fixed and flexible parts, which are defined by `blocks`, For example:
`parent.liquid`
```liquid
<html>
	<head>
		<title>{% block title %}The default title{% endblock %}</title>
		...
	</head>
	<body>
	{% block main %}
	{% endblock %}
	</body>
</html>
```

With `{% extends ... %}` statement, all your template allowed to have are just `blocks`: `{% block blockname %}...{% endblock %}`. Those blocks are used to replace the ones in the parent template.

If there are blocks in the parent template without one to replace with in current template, it will be used directly. For example:
```liquid
{% extends parent.liquid %}

{% block main %}
Main content
{% endblock %}
```
will be rendered with an HTML page with title "The default title"

You can also use `blocks` inside `blocks`. For example:

`parent.liquid`
```liquid
<html>
	<head>
		{% block head %}
		<title>{% block title %}The default title{% endblock %}</title>
		...
		{% endblock %}
	</head>
	<body>
	{% block main %}
	{% endblock %}
	</body>
</html>
```
This way you can replace the whole head or just the title with the blocks defined in your template respectively. Remember that once you have `{% block head %}` defined, the title block will be replaced anyway. To defined a new title, you should write it in your new head block:

```liquid
{% extends parent.liquid %}

{% block head %}
{# write the whole content of head here, including title #}
	<title>A new title</title>
	<!-- other content for head -->
{% endblock %}
```

!!! warning

	Blocks will be ignored in current template if they are not defined parent.

## File path of the template to be included/extended

You can use absolute and relative paths in `{% include ... %}` and `{% extends ... %}`. For relative paths, we will try to find the file relative to the current one. For example:
```
|- template.liquid
|- parents/
    |- mother.liquid
```
In `template.liquid` you can refer to `mother.liquid` by `{% extends parents/mother.liquid %}`

If current template is from a text, the current working directory will be used for the relative paths.

## Mode inheritance

You can define separate modes in each inclusion and they can be different from the current template. If not defined, it will inherited from the current template. For example:
`include1.liquid`
```liquid
{% mode loose %}
Hello {# comment to keep trailing spaces#}
```

`include1.liquid`
```liquid
World
```

```liquid
{% mode compact %}
{% include include1.liquid %}
{% include include2.liquid %}
```

will be rendered as `\nHello World`. The `\n` is coming from the one in `include1.liquid`

For inheritance, the contents in parent template are using the mode defined in itself, while in the current template, the blocks to replace the ones in the parent are using the one defined in the current template.

