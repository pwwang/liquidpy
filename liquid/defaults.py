"""Provide default settings/values"""
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .utils import PathTypeOrIter

# The default mode to initialize a Liquid object
# - standard: Compatible with standard liquid engine
# - wild: liquid- and jinja-compatible engine
# - jekyll: jekyll-compatible engine
MODE: str = "standard"

# Whether the template provided is a file path by default
FROM_FILE: bool = True

# Whether allow arguments of a filter to be separated
# by colon (:) with the filter
# e.g. {{ val | filter: arg1, arg2 }}
# jinja only supports:
# {{ val | filter(arg1, arg2)}}
FILTER_WITH_COLON = True

# The default search paths for templates
# support absolute paths
SEARCH_PATHS: "PathTypeOrIter" = ["/", "./"]

# The default format/language for the front matter
# Should be one of yaml, toml or json
FRONT_MATTER_LANG = "yaml"

# Available jinja Environment arguments
ENV_ARGS = [
    "block_start_string",
    "block_end_string",
    "variable_start_string",
    "variable_end_string",
    "comment_start_string",
    "comment_end_string",
    "line_statement_prefix",
    "line_comment_prefix",
    "trim_blocks",
    "lstrip_blocks",
    "newline_sequence",
    "keep_trailing_newline",
    "extensions",
    "optimized",
    "undefined",
    "finalize",
    "autoescape",
    "loader",
    "cache_size",
    "auto_reload",
    "bytecode_cache",
    "enable_async",
]

# In case some one wants to use nil
SHARED_GLOBALS = {"nil": None}

# Whether treat filters as globals
# Only works in wild mode
FILTERS_AS_GLOBALS = True
