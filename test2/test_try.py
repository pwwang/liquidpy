from liquid2.mild import parser

tpl = """A{% if x['a-b'] contains 'a' or false and false -%}
  123
{% endif %}B"""

parsed = parser.mild_parser.parse(tpl)
#print(parsed)
print(repr(parsed.render(x = {'a-b': 'abc'})))
