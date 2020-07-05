"""Tag liquid

{% liquid
if product.featured_image
  echo product.featured_image | img_tag
else
  echo 'product-1' | placeholder_svg_tag
endif %}
"""
from ..tagmgr import register_tag
from ..tag import Tag

@register_tag
class TagLiquid(Tag):
    """Class for tag else"""
    VOID = True
    SYNTAX = r"""
    inner_tag: tag_liquid
    !tag_liquid: $tagnames (_NL inner_tag | _NL tag_liquid_end_tag)+ _NL?
    ?tag_liquid_end_tag: "end" VAR
    """

    def t_tag_liquid(self, tagname, *tags):
        """Transformer for tag liquid"""
        # get rid of _NLs
        tags_no_tokens = []
        for tag in tags:
            if isinstance(tag, Tag):
                tag.context = self._context(tag.name)
                tags_no_tokens.append(tag)
            elif tag.strip():
                # endif
                tags_no_tokens.append(tag)
        return TagLiquid(tagname, (tags_no_tokens, self))

    def _post_starting(self):
        tags, orig_transformer = self.data
        new_transformer = orig_transformer.__class__(orig_transformer.parser,
                                                     self.level + 1)
        new_transformer.root = self
        for tag in tags:
            if isinstance(tag, Tag):
                new_transformer._starting_tag(tag)
            else:
                new_transformer.end_tag(tag, tag, tag)

    def _render(self, local_envs, global_envs):
        return self._children_rendered(local_envs, global_envs)
