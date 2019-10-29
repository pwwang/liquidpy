
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

__The above behavior of normal tags (tags without hyphen, `{%`, `{#`, `{{` and their compartments) are in `mixed` mode, which means it does not strip the whitespaces. This is a default mode of `liquidpy`. You may also change the default mode globally:__
```python
from liquid import defaults
defaults.LIQUID_DEFAULT_MODE = 'compact'
```

!!! note
    __By change the default mode to `compact`, then the whitespace tags will act exactly the same as the non-whitespace tags.__

    __You may also change the mode for each `Liquid` instance. Put `{% mode compact %}`, `{% mode mixed %}` or `{% mode loose %}` to tell the engine to use the corresponding mode.__

<div markdown="1" class="two-column">

Input:
```liquid
{% mode compact %}
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
