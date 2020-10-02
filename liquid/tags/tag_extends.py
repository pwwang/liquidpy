"""Tag extends

```liquid
{% extends ... %}
```
"""
from diot import Diot
from .manager import tag_manager
from .tag import Tag
from ..utils import template_meta, find_template
from ..exceptions import LiquidSyntaxError, LiquidRenderError

@tag_manager.register
class TagExtends(Tag):
    """The extends tag"""
    __slots__ = Tag.__slots__ + ('block_parsed', )

    VOID = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser.visitor.has_mother = True
        self.block_parsed = False

    def parse(self, force=False): # pylint: disable=unused-argument
        # type: (bool) -> None
        if self.parent.name != 'ROOT':
            raise LiquidSyntaxError(
                f'Must be first-level tag: {self!r}',
                self.context, self.parser
            )

        content = self.content
        # allows path to be quoted
        if len(content) > 2 and (
                content[:1] == content[-1:] == '"' or
                content[:1] == content[-1:] == "'"
        ):
            content = content[1:-1]

        try:
            mother = find_template(
                content,
                self.context.path,
                self.parser.config.extends_dir
            )
            if not mother or not mother.is_file():
                raise OSError
        except OSError:
            raise LiquidSyntaxError(
                'Mother template does not exist.', self.context, self.parser
            ) from None

        meta = template_meta(mother)
        # pylint: disable=attribute-defined-outside-init
        self.parsed = self.parser.__class__(
            meta,
            self.parser.config,
            Diot(name=meta.name,
                 path=meta.path,
                 stream=meta.stream,
                 lineno=0,
                 colno=0,
                 level=self.context.level+1)
        )
        self.parsed.parse()
        self.parsed.parent = self.parser
        # get the logger back
        self.parsed.config.update_logger()


    def _render(self, local_vars, global_vars):
        # type: (dict, dict) -> str
        """make sure the template is in the format of:
        {% extends ... %}
        {% block 1 %}...{% endblock %}
        {% block 2 %}...{% endblock %}
        there are no other tags other than a config/comment tag
        """
        # replace mother's blocks with self.parser's
        if not self.block_parsed:
            for blockname, block in self.parser.visitor.blocks.items():
                # block: current_block (replacement)
                # mother_block: mother's block (to replace)
                if blockname not in self.parsed.visitor.blocks:
                    raise LiquidRenderError(
                        f'Block {blockname!r} does not exist '
                        'in mother template',
                        block.context, block.parser
                    )
                mother_blocks = self.parsed.visitor.blocks
                mother_block = mother_blocks[blockname]
                # get the children of the block's parent
                siblings = mother_block.parent.children
                # get the index of the block in parent's children
                block_index = siblings.index(mother_block)
                # use the compacts of mother blocks
                block.open_compact = mother_block.open_compact
                block.close_compact = mother_block.close_compact
                # replace it with current block
                siblings[block_index] = block
                mother_blocks[blockname] = block
                # update the level to align with mother's logging structure
                block.context.level = mother_block.context.level
            self.block_parsed = True

        for blockname, block in self.parsed.visitor.blocks.items():
            block.parse_children(base_level=block.context.level)

        return self.parsed.visitor.root.render(local_vars, global_vars)[0]
