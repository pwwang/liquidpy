
`liquidpy` basically implements almost all the features supported by `liquid`. However, it has some differences and specific features due to the language feature itself.   
__Anything that is different from `liquid` will be bolded.__

# Tags
`liquidpy` supports all tags that `liquid` does: `{{`, `}}`, `{%`, `%}`, and their non-whitespace variants: `{{-`, `-}}`, `{%-` and `-%}`. __Beside these tags, `liquidpy` also recognizes `{#`, `#}` (non-whitespace variants: `{#-`, `-#}` have some comments in the template.__

# Operators, types, truthy and falsy
They basically follow `python` syntax. Besides that, `liquidpy` also has `true`, `false` and `nil` keywords as `liquid` does, which correspond to `True`, `False` and `None` in `python`.  