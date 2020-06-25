from lark import Lark

GRAMMER = r"""
start: node*

?node: expr_node | comment_node | open_node | close_node | literal_node

expr_node: EXPR_NODE
comment_node: COMMENT_NODE
open_node: OPEN_NODE
close_node: CLOSE_NODE
literal_node: LITERAL_NODE

LITERAL_NODE.-99: /.+?(?=\{[\{%#]|$)/s
EXPR_NODE: /\{\{-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?\}\}/s
CLOSE_NODE.2: /\{%-?\s*end.*?-?%\}/s
OPEN_NODE: /\{%-?('.*?(?<!\\)(\\\\)*?'|".*?(?<!\\)(\\\\)*?"|.*?)*?-?%\}/s
COMMENT_NODE: /\{\#-?.*?-?\#\}/s
"""

parser = Lark(GRAMMER, parser="lalr")

test_template = """awfew{% abc
xxx "%}"
 %}
{# 123 #}
{% endif -%}
{{ "}}\\"" }}
ddd"""

print(parser.parse(test_template).pretty())
