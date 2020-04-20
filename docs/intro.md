`liquidpy` basically implements almost all the features supported by `liquid`. However, it has some differences and specific features due to the language feature itself.

!!! note

    The bolded in the documentation is mentioning the differences between `liquid` and `liquidpy`

# Tags

`liquidpy` supports all tags that `liquid` does: `{{`, `}}`, `{%`, `%}`, and their non-whitespace variants: `{{-`, `-}}`, `{%-` and `-%}`. __Beside these tags, `liquidpy` also recognizes `{#`, `#}` (non-whitespace variants: `{#-`, `-#}` have some comments in the template.__

# Nodes

Based on tags, there are 4 different types of nodes:

- `Expression nodes`: `{{ ... }}` and its non-whitespace variants
- `Comment nodes`: `{# ... #}` and its non-whitespace variants
- `Literal nodes`: Anything that literally exported to the output
- `Statement nodes`: `{% ... %}` and its non-whitespace variants

!!! note

    In this documentation, if undecleared, `nodes` will be referred to `statement nodes`
