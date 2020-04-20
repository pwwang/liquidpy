
Same as liquid does, you can include a hyphen in your tag syntax `{{-`, `-}}`, `{%-`, `-%}`, `{#-` and `-#}` to strip whitespace from the left or right side of a rendered tag.
They basically strip the whitespace before and after the tag, as well as the newline character in the line of the tag.

<div markdown="1" class="two-column">

Input:
```liquid
{% assign my_variable = "tomato" %}
{{ my_variable }}
```

</div>
<div markdown="1" class="two-column">

Output:
```ini
[empty line]
tomato
```

</div>

---

<div markdown="1" class="two-column">

```liquid
{%- assign my_variable = "tomato" -%}
{{ my_variable }}
```

</div>
<div markdown="1" class="two-column">

```
tomato
```

</div>

---


<div markdown="1" class="two-column">

```liquid
{% assign username = "John G. Chalmers-Smith" %}
{% if username and len(username) > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}
```

</div>
<div markdown="1" class="two-column">

```ini
[empty line]
[empty line]
  Wow, John G. Chalmers-Smith, you have a long name!
[empty line]
```
</div>

---

<div markdown="1" class="two-column">

```liquid
{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and username.size > 10 -%}
  Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif -%}
```

</div>
<div markdown="1" class="two-column">

```
  Wow, John G. Chalmers-Smith, you have a long name!
```

</div>

---

<div markdown="1" class="two-column">

```liquid
{%- assign username = "John G. Chalmers-Smith" -%}
{%- if username and username.size > 10 -%}
  Wow, {{ username }}, you have a long name!
{%- else -%}
  Hello there!
{%- endif %}
```

</div>
<div markdown="1" class="two-column">

```
  Wow, John G. Chalmers-Smith, you have a long name!
[empty line, due to the compond tag '%}' instead of '-%}']
```

</div>
---

!!! note
    __the leading spaces of the line is not stripped, this is slightly different from `liquid`__

__The above behavior of normal tags (tags without hyphen, `{%`, `{#`, `{{` and their compartments) are in `loose` mode, which means it does not strip the whitespaces. This is a default mode of `liquidpy`. You may also change the default mode for the `Liquid` object:__

```python
liq = Liquid("...", liquid_mode='compact')
```

!!! note
    __By changing the default mode to `compact`, then the whitespace tags will act exactly the same as the non-whitespace tags.__

    __You may also change the mode for each template or even part of them. Just put `{% config mode="compact" %}` in your template, and then the later part of the template will be parsed in such mode

!!! warning

    `{% mode compact %}` node is deprecated, use `config` node instead

<div markdown="1" class="two-column">

Input:
```liquid
{% config mode="compact" %}
{% assign username = "John G. Chalmers-Smith" %}
{% if username and username.size > 10 %}
  Wow, {{ username }}, you have a long name!
{% else %}
  Hello there!
{% endif %}
```

</div>
<div markdown="1" class="two-column">

Output:
```
  Wow, John G. Chalmers-Smith, you have a long name!
```

</div>

---

!!! note
    ___Unless decleared explictly, the mode will be `compact` in this document.___
