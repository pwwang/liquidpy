"""Tag config

```liquid
{% config  %}
```
"""
from lark import v_args
from .manager import tag_manager
from .tag import Tag
from .transformer import TagTransformer
from ..utils import find_dir
from ..exceptions import LiquidRenderError

@v_args(inline=True)
class TagConfigTransformer(TagTransformer):
    """The transformer for tag config"""
    # pylint: disable=no-self-use
    def tag_config(self, *items):
        """Transform the tag_config rule"""
        return dict(items)

    def config_item(self, varname, constant=True):
        """Transform the tag_config rule"""
        return varname, constant

@tag_manager.register
class TagConfig(Tag):
    """The config tag"""
    VOID = True
    SECURE = False

    START = 'tag_config'
    GRAMMAR = '''
    tag_config: config_item+
    config_item: var ("=" constant)?
    '''
    TRANSFORMER = TagConfigTransformer()

    def parse(self, force=False):
        # type: (bool) -> None
        """Parse the configurations"""
        super().parse(force=force)
        config = self.parser.config.copy()
        # vname is token
        for vname, value in self.parsed.items():
            varname = str(vname)
            if varname not in config:
                if vname.line > 1:
                    self.context.lineno += vname.line - 1
                    self.context.colno = vname.column - 1
                else:
                    self.context.colno += vname.column - 1

                raise LiquidRenderError(
                    f"No such configuration item: {varname!r}",
                    self.context, self.parser
                )

            if varname == 'strict':
                raise LiquidRenderError(
                    "Configuration item 'strict' is not allowed to "
                    "be modified by 'config' tag.",
                    self.context, self.parser
                )

            if varname == 'debug':
                config.debug = value
                config.update_logger()
            elif varname in ('extends_dir', 'include_dir'):
                directory = find_dir(value, self.context.path)
                if not directory:
                    if vname.line > 1:
                        self.context.lineno += vname.line - 1
                        self.context.colno = vname.column - 1
                    else:
                        self.context.colno += vname.column - 1
                    raise LiquidRenderError(
                        f"Cannot find the directory for {varname!r}",
                        self.context, self.parser
                    )
                config[varname] = config[varname][:] + [directory]
            else:
                config[varname] = value
        self.parser.config = config

    # pylint: disable=unused-argument
    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        return ''
