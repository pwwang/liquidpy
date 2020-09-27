"""Tag include

```liquid
{% include ... %}
```
"""
from diot import Diot
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .transformer import TagTransformer, render_segment
from ..utils import template_meta, find_template
from ..exceptions import LiquidSyntaxError

@v_args(inline=True)
class TagIncludeTransformer(TagTransformer):
    """The transformer for tag include"""
    # pylint: disable=no-self-use
    def include_item(self, varname, test):
        """Transform include_item rule"""
        return (str(varname), test)

    def tag_include(self, path, *items):
        """Transform tag_include"""
        return (path, items)

@tag_manager.register
class TagInclude(Tag):
    """The extends tag"""
    VOID = True

    START = 'tag_include'
    GRAMMAR = """
    tag_include: (string|/[^\\s]+/) (include_item)*
    include_item: varname "=" test
    """
    TRANSFORMER = TagIncludeTransformer()

    def parse(self, force=False):
        # type: (bool) -> None
        """Parse the include template"""
        if not super().parse(force):
            return
        path = self.parsed[0] # pylint: disable=access-member-before-definition
        path = str(path)
        try:
            include_template = find_template(
                path,
                self.context.path,
                self.parser.config.include_dir
            )
            if not include_template or not include_template.is_file():
                raise OSError
        except OSError:
            raise LiquidSyntaxError(
                f'Cannot find template: {path!r} ({self!r})',
                self.context, self.parser
            ) from None

        meta = template_meta(include_template)

        inc_parser = self.parser.__class__(
            meta,
            self.parser.config,
            Diot(name=meta.name,
                 stream=meta.stream,
                 path=meta.path,
                 colno=0,
                 lineno=0,
                 level=self.context.level + 1)
        )
        inc_parser.parse()
        inc_parser.parent = self.parser
        inc_parser.config.update_logger()
        # pylint: disable=attribute-defined-outside-init
        self.parsed = inc_parser, self.parsed[1]

    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        inc_parser, items = self.parsed
        items = dict(items)
        for varname, value in items.items():
            items[varname] = render_segment(value, local_vars, global_vars)

        local_vars_copy = local_vars.copy()
        local_vars_copy['include'] = items

        return inc_parser.visitor.root.render(local_vars_copy, global_vars)[0]
