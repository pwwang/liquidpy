import sys
from pathlib import Path
sys.path.insert(0, Path(__file__).parent.parent.resolve().as_posix())
from liquid import Liquid

tpl = """A{% for i in x %}
{% if i == 1 %}}1
{% elsif i == 2 %}}2
{% elsif i == 3 %}}3
{% endif %}
{% endfor %}B"""

liq = Liquid(tpl)
#print(parsed)
print(repr(liq.render(x = [1,2,3])))
