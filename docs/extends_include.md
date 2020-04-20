# Template inclusion and inheritance

## Inclusion
You can put {% include ... %} somewhere in your template to include the content of another template.

~~It can be even put in a statement block. For example:~~
```diff
- The calculated X value is:
- {% include calculate_x.liquid %}
- {{x}}
```

~~`calculate_x.liquid`~~
```diff
- {% assign x = x * 10 %}
```

```diff
- # without the include statement
- # liquid.render(x = 1) == '1'
- # but with it:
- liquid.render(x = 1) == '10'
```

!!! warning

	Since `v0.5.0`, variables can no longer be modified in a included template.
	And you can't refer to any variables inside the included template in later part of the parent template.

!!! hint

	- You can also use `{% include ... %}` inside a template to be included
	- You can, but don't have to use quote for the included file path

Since `v0.5.0`, you can pass variables to included templates, while, it still has access to the variables in parent template, but is not able to modify them.

!!! hint

	To use variables with the same name, you can just pass the variable name. You can modify them, however, it taks no effect on the variables in parent template.

For example:

`calculate_x.liquid`
```liquid
{% assign x = x * 10 %}
```

```python
Liquid("""
{% assign x = 1 %}
{% include calculate_x.liquid %}
{{x}}
""").render()
# Error: Variable referenced before assignment
# x is a global variable in include without global statement

Liquid("""
{% assign x = 1 %}
{% include calculate_x.liquid x %}
{{x}}
""").render()
# OK, but prints 1
```

### Directories to scan

- The directory where the parent template is has always the highest priority
- You can specify directories to scan in parent template by
  ```liquid
  {% config include="/absolute/path; relative/path1; ../rel/path2" %}
  ```
  The absolute paths will be used directly, whereas the relative paths will be parsed based on where the parent template is.
- If the parent template is from a string or stream, current working directory will be used.
- You can also specify some common directories when initializing the `Liquid` object
  ```
  Liquid("...", liquid_include="path1; path2...")
  ```
- Later added paths will be scanned first
- Current working directory is also available for scanning with the lowest priority unless re-added later.

## Inheritance

~~A template can be inherited from a parent template. You just need to put `{% extends ... %}` at the top of the template or at the second place while the first is `{% mode ... %}`~~

Since `v0.5.0`, `extends` node can be put anywhere in the template

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

With `{% extends ... %}` statement, template will have `blocks`: `{% block blockname %}...{% endblock %}`, which will be used to replace the blocks in mother template.

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

### Directories to scan

Basically the same as `include`, only that `./` is not always available for scanning unless you add them by yourself.

## Changing configurations in different templates

In included templates or mother templates to extend, you can change all the items for configurations: `mode`, `loglevel`, `include` and `extends`.

Note that if loglevel is defined in current template, when the parser returns, the loglevel will be resumed if it has been changed somewhere else.

!!! note

	`{% config include=... extends=... %}` will be accumulated during the parsing path. But later-added paths have the priority. So if you have ambigous paths already added, make the add the one you desire very close to where you have your `include` or `extends` nodes
