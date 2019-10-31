# 0.2.0
- Add inclusion and inheritance support
- Add `cycle` for `for` loop

# 0.1.0
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

# 0.0.7
- Allow `{% mode %}` block to be anywhere in the source code
- Full the coverage
- Change support only for python3.5+

# 0.0.6
- Add modifiers `&` and `*` to allow chaining and expanding arguments