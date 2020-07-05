"""Tag echo

{% liquid
if product.featured_image
  echo product.featured_image | img_tag
else
  echo 'product-1' | placeholder_svg_tag
endif %}
"""
from ..tagmgr import register_tag
from ..tagfrag import try_render
from ..tag import Tag

@register_tag
class TagEcho(Tag):
    """Class for tag else"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_echo
    !tag_echo: $tagnames output
    """

    def t_tag_echo(self, tagname, output):
        """Transformer for tag echo"""
        return TagEcho(tagname, output)

    def _render(self, local_envs, global_envs):
        output = try_render(self.data, local_envs, global_envs)
        return str(output) if output is not None else ''
