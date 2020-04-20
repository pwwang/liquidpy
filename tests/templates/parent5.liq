{% config mode=compact, loglevel=info %}

{% block b0 %}
empty block
{% endblock %}


{% block b1 %}
{% capture x %}
{% if true %}
1
{% endif %}
{% endcapture %}
{% endblock %}
