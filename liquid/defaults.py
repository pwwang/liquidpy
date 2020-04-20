"""
Default settings for liquidpy
See source of `liquid/defaults.py`
"""
import logging
# The logger name for liquidpy
LIQUID_LOGGER_NAME = 'liquidpy'
# Default mode
LIQUID_DEFAULT_MODE = 'loose'

# Open tag for statements {% assign x = 1 %}
LIQUID_STATE_OPENTAG = '{%'
# Compact open tag for statements {%- assign x = 1 %}
LIQUID_STATE_OPENTAG_COMPACT = '{%-'
# Countpart of LIQUID_STATE_OPENTAG
LIQUID_STATE_CLOSETAG = '%}'
# Countpart of LIQUID_STATE_OPENTAG_COMPACT
LIQUID_STATE_CLOSETAG_COMPACT = '-%}'
# Open tag for expressions
LIQUID_EXPR_OPENTAG = '{{'
# Compact open tag for expressions
LIQUID_EXPR_OPENTAG_COMPACT = '{{-'
# Countpart of LIQUID_EXPR_OPENTAG
LIQUID_EXPR_CLOSETAG = '}}'
# Countpart of LIQUID_EXPR_OPENTAG_COMPACT
LIQUID_EXPR_CLOSETAG_COMPACT = '-}}'
# Open tag for comments
LIQUID_COMMENT_OPENTAG = '{#'
# Compact open tag for comments
LIQUID_COMMENT_OPENTAG_COMPACT = '{#-'
# Countpart of LIQUID_COMMENT_OPENTAG
LIQUID_COMMENT_CLOSETAG = '#}'
# Countpart of LIQUID_COMMENT_OPENTAG_COMPACT
LIQUID_COMMENT_CLOSETAG_COMPACT = '-#}'

# All paired tags, use for searching countparts
LIQUID_PAIRED_TAGS = [
    ((LIQUID_STATE_OPENTAG, LIQUID_STATE_OPENTAG_COMPACT),
     (LIQUID_STATE_CLOSETAG, LIQUID_STATE_CLOSETAG_COMPACT)),
    ((LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT),
     (LIQUID_EXPR_CLOSETAG, LIQUID_EXPR_CLOSETAG_COMPACT)),
    ((LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT),
     (LIQUID_COMMENT_CLOSETAG, LIQUID_COMMENT_CLOSETAG_COMPACT)),
]
# All open tags
LIQUID_OPEN_TAGS = (LIQUID_STATE_OPENTAG,
                    LIQUID_STATE_OPENTAG_COMPACT,
                    LIQUID_EXPR_OPENTAG,
                    LIQUID_EXPR_OPENTAG_COMPACT,
                    LIQUID_COMMENT_OPENTAG,
                    LIQUID_COMMENT_OPENTAG_COMPACT)
# All close tags
LIQUID_COMPACT_TAGS = (LIQUID_STATE_OPENTAG_COMPACT,
                       LIQUID_STATE_CLOSETAG_COMPACT,
                       LIQUID_EXPR_OPENTAG_COMPACT,
                       LIQUID_EXPR_CLOSETAG_COMPACT,
                       LIQUID_COMMENT_OPENTAG_COMPACT,
                       LIQUID_COMMENT_CLOSETAG_COMPACT)

# The main function name in compiled source
LIQUID_RENDER_FUNC_PREFIX = '_liquid_render_function'
# The name of the compiled source, will be shown in tracebacks
LIQUID_COMPILED_SOURCE_NAME = '<LIQUID_COMPILED_SOURCE>'
# The name of the context lines to show in debug
LIQUID_DEBUG_SOURCE_CONTEXT = 5
# Max call stacks allow in template,
# call stacks triggered by include and extends
LIQUID_MAX_STACKS = 100
# The file name to show in debug
# if primary template is text (instead of a file)
LIQUID_TEXT_FILENAME = '<LIQUID TEMPLATE SOURCE>'
# If template is from a stream
# the name to show in the stacks
LIQUID_STREAM_FILENAME = '<LIQUID TEMPLATE STREAM>'
# default log level
LIQUID_LOGLEVEL_DETAIL = "DETAIL"
LIQUID_LOGLEVELID_DETAIL = 15

# The variable name of list of compiled string
LIQUID_RENDERED = '_liquid_rendered'
# The append function of above list
LIQUID_RENDERED_APPEND = '_liquid_ret_append'
# The extend function of above list
LIQUID_RENDERED_EXTEND = '_liquid_ret_extend'

# The argument name of the main function
LIQUID_CONTEXT = '_liquid_context'
# The name of the dictionary of all liquid filters
LIQUID_LIQUID_FILTERS = '_liquid_liquid_filters'
# The default environment
LIQUID_DEFAULT_ENVS = {
    'true': True,
    'false': False,
    'nil': None,
}

# the registered nodes
# name => Node class
LIQUID_NODES = {}

logging.addLevelName(LIQUID_LOGLEVELID_DETAIL, LIQUID_LOGLEVEL_DETAIL)
# just in case somebody is using DETAILS, then
# all messages with DETAIL should also be showing
logging.addLevelName(LIQUID_LOGLEVELID_DETAIL - 1,
                     LIQUID_LOGLEVEL_DETAIL + "S")
