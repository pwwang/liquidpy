{% mode compact%}
{% extends parent3.liq %}

{% block b1 %}
abc
	{% block b2 %}
	def
	{% endblock %}
hij
{% endblock %}
