
You may checkout the documentation for jekyll liquid:

- https://jekyllrb.com/docs/liquid/

The compatibility issues list on:

- https://pwwang.github.com/liquidpy/standard

also applied in jekyll mode. Besides, passing variables to a sub-template using `include` tag is not supported. Instead, please using jinja's `with` tag:

- https://stackoverflow.com/a/9405157/5088165
