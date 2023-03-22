# Change Log

## 0.8.0

- ⬆️ Upgrade deps including markdown, regex, and python-slugify
- 📌 Drop support for python3.6
- 🐛 Fix passing `env` to `Liquid()` not working

## 0.7.6

- 🐛 Fix JSON/list parsing in certain cases (#50)

## 0.7.5

- ✨ Implement a playground powered by pyscript
- ✨ Add filter `call` for `wild` mode

## 0.7.4

- ✅ Add tests regarding #47
- 📌 Upgrade and pin dependencies

## 0.7.3

- 🩹 Make `default` filter work with `None`
- 🩹 Make `attr` filter work with dicts
- 🩹 Use filter `liquid_map`, in wild mode, instead of `map`, which is overridden by python's builtin `map`

## 0.7.2

- 🐛 Fix `date` filter issues (#38, #40)
- ✨ Add `markdownify` for jekyll (#36, #37)
- ✨ Add `number_of_words` for jekyll
- ✨ Add jekyll filter `sort`
- ✨ Add jekyll filter `slugify`
- ✨ Add jekyll filter `array_to_sentence_string`
- ✨ Add jekyll filter `jsonify`
- ✨ Add jekyll filters `xml_escape`, `cgi_escape` and `uri_escape`
- ✨ Add `int`, `float`, `str` and `bool` as both filters and globals for all modes (#40)

## 0.7.1

- ✨ Add `regex_replace` filter
- ✨ Allow absolute path and pathlib.Path passed as template files
- ✨ Allow `+/-` to work with date filter (#38)
- ✨ Add `filters_as_globals` for wild mode (defaults to `True`)

## 0.7.0

- Reimplement using jinja2

## 0.6.4

Last release of 0.6, for compatibilities.

- Add regex_replace filter (#33)

## 0.6.3

- Allow tag for to have output(test | filter) in python mode.
- Fix stacks not print in some cases.
- Avoid closing stream after parsing
- Add better error message for attribute error while rendering
- Print 'KeyError' for render error if it is a KeyError.

## 0.6.2

- Update dependency versions

## 0.6.1

- Fix use of LiquidPython
- Add getitem and render filter for python mode
- Fix EmptyDrop for variable segment in python mode
- Fix re-rendering error for extends tag (#29)

## 0.6.0

- Remodel the package to use a lexer to scan the nodes first and then lark-parse to parse the tag.

## 0.5.0

- Extract major model of node to allow `register_node` (#18)
- Introduce `config` node and deprecate `mode`
- Allow specification of directories to scan for `include` and `extends` (#19)
- Add loglevel `detail` to enable verbosity between `info` and `debug`
- Allow passing variables to included templates (#8)
- Disallow variables in parent templates to be modified in included templates
- Require backtick ``( ` )`` for liquidpy expression to be used in statement nodes
- Add API documentations

## 0.4.0

- Implement issue #13: Adding ternary end modifier (`$`)
- Expand list/dict context in debug information

## 0.3.0

- Force explict modifiers (=/!) for True/False action in ternary filters
- Add combined ternary filters
- Add shortcut `?` for `?bool`
- Use the maximum lineno on traceback instead of the last one.

## 0.2.3

- Fix parsing errors when unicode in a template loaded from text #10 (thanks to vermeeca)

## 0.2.2

- Show shortened context in debug information
- Fix #9: stream cursor shifted when unicode in the template.

## 0.2.1

- Fix #7: forloop problem with nesting for statements
- Fix other bugs

## 0.2.0

- Add inclusion and inheritance support
- Add `cycle` for `for` loop

## 0.1.0

- Rewrite whole engine using a stream parser
- Support multi-line for statements, expressions and tag comments (#1)
- Support wrapper (instead of a single prefix) for statement comments
- Add `from` and `import` shortcuts to import python modules
- Support expressions in `if/unless/while` statements
- Support `liquid` `forloop` object for `for` statement (#2)
- Improve debug information
- Add arguemtn position specification for filters
- Add tenary filters
- Remove `&` modifiers

## 0.0.7

- Allow `{% mode %}` block to be anywhere in the source code
- Full the coverage
- Change support only for python3.5+

## 0.0.6

- Add modifiers `&` and `*` to allow chaining and expanding arguments
