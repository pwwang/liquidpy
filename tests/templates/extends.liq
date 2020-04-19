{% config mode=compact %}
{% extends parent5.liq %}

{% block b1 %}
abc
	{% block b2 %}
	def
	{% endblock %}
hij
{% endblock %}
