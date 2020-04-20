## liquid.nodes


- **desc**

	Nodes in liquidpy

!!! abstract "method: `check_quotes(value)`"

	Check if value is correctly quoted or not quoted:
	True: <empty string>
	True: <unquoted string>
	False: 'abc <compond quote>
	False: "abc <compond quote>
	False: "abc' <compond quote>
	False: 'abc" <compond quote>

	- **params**

		- `value (string)`:  The value to check

	- **returns**

		- `(bool)`:  True if value is correctly quoted otherwise False

!!! abstract "method: `compact(string, left, right)`"

	Apply compact mode to the string

	- **params**

		- `string (str)`:  The string to apply compact mode

		- `left (bool)`:  If the left side of the string should be compacted

		- `right (bool)`:  If the right side of the string should be compacted

	- **returns**

		- `(str)`:  The string with compact mode applied

!!! abstract "method: `parse_mixed(mixed, shared_code)`"

	Parse mixed expressions like 1 + `a | @plus: 1`

	- **params**

		- `mixed (str)`:  The mixed expression to be parsed

		- `shared_code (LiquidCode)`:  A LiquidCode object needed

		    by `NodeLiquidExpression`

	- **returns**

		- `(str)`:  The parsed expression

!!! abstract "method: `register_node(name, klass)`"

	Register a new node
	To unregister a node:
	```
	from liquid.defaults import LIQUID_NODES
	del LIQUID_NODES[<name>]
	```

	- **params**

		- `name (string)`:  The name of the node, will be match at `{% <name> ...`

		- `klass (type)`:  The class the handle the nodes

!!! abstract "method: `scan_file(relpath, dirs, reverse)`"

	Scan a file in the dirs

	- **params**

		- `relpath (str)`:  The relative path

		- `dirs (list)`:  The list of directories to scan

		- `reverse (bool)`:  Scan the last directory in the list first?

	- **returns**

		- `(Path)`:  The file found in the `dirs`

!!! abstract "method: `unquote(value)`"

	Remove quotes from a string
	Assuming it's checked by check_quotes

	- **params**

		- `value (str)`:  The value to be unquoted

	- **returns**

		- `(str)`:  The unquoted value

!!! example "class: `Node`"

	Nodes need to be closed
	For example: {% if ... %} ... {% endif %}

	!!! abstract "method: `end(self, name)`"

		End the node, check if I am the right end node to close.

	!!! abstract "method: `parse_node(self)`"

		Returns False to parse content as literal
		Otherwise as normal liquid template

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeAssign`"

	Node like {% assign a = `1 | @plus: 1` %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeBlock`"

	Node {% block ... %} {% endblock %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeBreak`"

	Node {% break %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeCapture`"

	Node like {% capture x %} ... {% endcapture %}

	!!! abstract "method: `parse_node(self)`"

		Start a new code to save the content generated in the content

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeCase`"

	Node like {% case x %} ... {% endcase %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeComment`"

	Node {% comment ... %} ... {% endcomment %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeConfig`"

	Node {% config mode="compact" include=".." loglevel="info" %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeBreak`"

	Node {% break %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeCycle`"

	Node {% cycle ... %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeDecrement`"

	Node like {% increment y %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeElse`"

	Node {% else %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeElseif`"

	Node {% elseif .. %}, {% elif .. %} and {% elsif ... %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeExtends`"

	Node {% extends ... %}

	!!! abstract "method: `parse_node(self)`"

		Parse the node into python codes, and add them to `self.code`
		for execution

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeFor`"

	Node '{% for ... %} {% endfor %}'

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeFrom`"

	Node {% from ... import ... %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeIf`"

	Node {% if ... %} ... {% endif %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeImport`"

	Node {% import ... %}

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeInclude`"

	Node {% include ... %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeIncrement`"

	Node like {% increment x %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeIntact`"

	Content intact node, where the content remains
	unparsed as liquid template.
	The content is grabbed between {% raw %} and {% endraw %}, which
	will then be parsed in parse_content

	- **params**

		- `content (str)`:  The content between open and close node

		- `lineno (int)`:  The line number when the node hit, as `context.lineno`

		    will be changed during further parsing

		- `compact_left (bool)`:  Whether the left side of `content` should

		    be compact

		- `compact_right (bool)`:  Whether the right side of `content` should

		    be compact

	!!! abstract "method: `end(self, name)`"

		End the node, check if I am the right end node to close.

	!!! abstract "method: `parse_content(self)`"

		Add debug information that I am parsing the content

	!!! abstract "method: `parse_node(self)`"

		Returns False to parse content as literal
		Otherwise as normal liquid template

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeLiquidComment`"

	Node like {# ... #}

	!!! abstract "method: `parse_node(self)`"

		Parse the node into python codes, and add them to `self.code`
		for execution

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeLiquidLiteral`"

	Any literals in the template

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodePython`"

	Node like {% python a = 1 %} and {% python %}a = 1{% endpython %}

	!!! abstract "method: `end(self, name)`"

		End the node, check if I am the right end node to close.

	!!! abstract "method: `parse_content(self)`"

		Parse the content between {% python %} and {% endpython %}

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeRaw`"

	Node {% raw %} ... {% endraw %}

	!!! abstract "method: `end(self, name)`"

		End the node, check if I am the right end node to close.

	!!! abstract "method: `parse_node(self)`"

		Returns False to parse content as literal
		Otherwise as normal liquid template

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeUnless`"

	Node like {% unless x %} ... {% endunless %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeVoid`"

	Nodes without ending/closing
	For example: {% config mode="compact" include="xxx" %}

	- **params**

		- `name (str)`:  The name of the node, will be matched at `{% <name>`

		- `attrs (str)`:  The rest string of the node other than name

		- `code (LiquidCode)`:  The LiquidCode object to save the codes

		- `shared_code (LiquidCode)`:  The LiquidCode object to save some

		    shared codes

		- `config (LiquidConfig)`:  The LiquidConfig object with the configurations

		- `context (diot.Diot)`:  The context of this node

	!!! abstract "method: `parse_node(self)`"

		Parse the node into python codes, and add them to `self.code`
		for execution

	!!! abstract "method: `start(self)`"

		Node hit. Start validating the node and preparing for parsing

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeWhen`"

	Node {% when ... %} in case

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression

!!! example "class: `NodeIf`"

	Node {% if ... %} ... {% endif %}

	!!! abstract "method: `try_mixed(self, mixed)`"

		Try to parse mixed expression using my shared_code

		- **params**

			- `mixed (str)`:  The mixed expression to be parsed

		- **returns**

			- `(str)`:  The parsed expression
## liquid.expression


- **desc**

	Parse the expression node {{ ... }}

	Expression nodes could be complicated, we put this in a separate model
## liquid.code


- **desc**

	Code object for liquidpy

!!! example "class: `LiquidCode`"

	Build source code conveniently.

	!!! abstract "method: `__init__(self, indent)`"

		Constructor of code builder

		- **params**

			- `indent (int)`:  The initial indent level

	!!! abstract "method: `add_code(self, code)`"

		Add a LiquidCode object to the code.
		Indentation and newline will be added for you, don't provide them.

		- **params**

			- `code (LiquidCode)`:  The LiquidCode object to add

	!!! abstract "method: `add_line(self, line, context)`"

		Add a line of source to the code.
		Indentation and newline will be added for you, don't provide them.

		- **params**

			- `line (str)`:  The line to add

	!!! abstract "method: `dedent(self)`"

		Decrease the current indent for following lines.

	!!! abstract "method: `get_line(self, lineno)`"

		Get the line with lineno (0-based)

		- **params**

			- `lineno`:  The line number

		- **returns**

			- `(LiquidLine)`:  The line at `lineno`

	!!! abstract "method: `indent(self)`"

		Increase the current indent for following lines.

	!!! abstract "method: `tag(*args, **kwds)`"

		Make sure the code with the given tag only added once

		- **params**

			- `codetag (str)`:  The tag of the codes to be added

!!! example "class: `LiquidLine`"

	Line of compiled code
	

	- **params**

		- `line (str)`:  The line in string format

		- `context (diot.Diot)`:  The context object

		    - filename: The filename

		    - lineno: The line number in template source

		    - <other context> may not be used in this object

		- `ndent (int)`:  The indentation level of this line
## liquid.parser


- **desc**

	

	The parser for liquidpy

!!! example "class: `LiquidParser`"

	Parse a file or a string template

	!!! abstract "method: `__init__(self, filename, prev, config, stream, shared_code, code)`"

		Constructor for LiquidParser

		- **params**

			- `filename (str)`:  The filename of the template

			- `prev (LiquidParse)`:  The previous parser

			- `config (LiquidConfig)`:  The configuration

			- `stream (stream)`:  The stream to parse instead of the file of filename

			- `shared_code (LiquidCode)`:  The shared code

			- `code (LiquidCode)`:  The code object

	!!! abstract "method: `assemble(self, context)`"

		Assemble it to executable codes, only when final is True
		This may be re-assembled with different context
		So we should not do anything with self.code and self.shared_code

		- **params**

			- `context (diot)`:  The context to render the template

	!!! abstract "method: `call_stacks(self, lineno)`"

		Get call stacks for debugging

		- **params**

			- `lineno (int)`:  Current line number

		- **returns**

			- `(list)`:  The assembled call stacks

	!!! abstract "method: `parse(self)`"

		Start parsing the template

	!!! abstract "method: `parse_comment(self, tag)`"

		Parse the comment tag `{##}` or `{#--#}`

		- **params**

			- `tag (str)`:  The open tag.

	!!! abstract "method: `parse_expression(self, tag)`"

		Parse the expressions like `{{ 1 }}`

		- **params**

			- `tag (str)`:  The open tag

	!!! abstract "method: `parse_literal(self, string, tag)`"

		Parse the literal texts

		- **params**

			- `string (str)`:  The literal text

			- `tag (str)`:  The end tag

	!!! abstract "method: `parse_statement(self, tag)`"

		Parse the statement node `{% ... %}`

		- **params**

			- `tag (str)`:  The open tag
## liquid.filters


- **desc**

	

	Built-in filters for liquidpy
## liquid.exceptions


- **desc**

	

	Exceptions used in liquidpy

!!! example "class: `LiquidCodeTagExists`"

	Raises when codes with tag has already been added

!!! example "class: `LiquidExpressionFilterModifierException`"

	When incompatible modifiers are assigned to a filter

!!! example "class: `LiquidNameError`"

	When an invalid variable name used

!!! example "class: `LiquidNodeAlreadyRegistered`"

	When a node is already registered

!!! example "class: `LiquidRenderError`"

	Raises when the template fails to render

!!! example "class: `LiquidSyntaxError`"

	Raises when there is a syntax error in the template
## liquid.defaults


- **desc**

	

	Default settings for liquidpy

	See source of `liquid/defaults.py`
## liquid.stream


- **desc**

	

	Stream helper for liquidpy

!!! abstract "method: `safe_split(string, delimiter, limit, trim, wraps, quotes, escape)`"

	Safely split a string

	- **params**

		- `string (str)`:  The string to be split

		- `delimit (str)`:  The delimiter

		- `limit (int)`:  The limit of split

		- `wraps (list)`:  A list of paired wraps to skip of the delimiter             is wrapped by them

		- `quotes (str)`:  A series of quotes to skip of the delimiter is             wrapped by them

		- `escape (str)`:  The escape character to see             if any character is escaped

	- **returns**

		- `(list)`:  The split strings

!!! abstract "method: `words_to_matrix(words)`"

	Convert words to matrix for searching.
	For example:
	```
	['{%', '{%-', '{{'] => [
	    {'{': 0},     3 shares, 0 endings
	    {'%': 1, '{': 1},
	    {'-': 1}
	]
	```

	- **params**

		- `words`:  The words to be converted

	- **returns**

		- `(list)`:  The converted matrix

!!! example "class: `LiquidStream`"

	The stream helper for liquidpy

	!!! abstract "method: `__init__(self, stream)`"

		Initialize the stream

		- **params**

			- `stream (Stream)`:  A python stream

	!!! note "property: `cursor`"

		The current position in the stream

		- **returns**

			- `(int)`:  An opaque number representing the current position.

	!!! abstract "method: `close(self)`"

		Close the stream

	!!! abstract "method: `dump(self)`"

		Dump the rest of the stream

		- **returns**

			- `(str)`:  The rest of the stream

	!!! abstract "method: `eos(self)`"

		Tell if the stream is ended

		- **returns**

			- `(bool)`:  `True` if it is else `False`

	!!! abstract "method: `from_file(path)`"

		Get stream of a file

		- **params**

			- `path (str)`:  The path of the file

		- **returns**

			- `(LiquidStream)`:  A LiquidStream object

	!!! abstract "method: `from_stream(stream)`"

		Get stream of a stream

		- **params**

			- `stream (Stream)`:  A stream

		- **returns**

			- `(LiquidStream)`:  A LiquidStream object

	!!! abstract "method: `from_string(string)`"

		Get stream of a string

		- **params**

			- `string (str)`:  The string

		- **returns**

			- `(LiquidStream)`:  A LiquidStream object

	!!! abstract "method: `get_context(self, lineno, context, startno)`"

		Get the line of source code and its context

		- **params**

			- `lineno  (int)`:  Line number of current line

			- `context (int)`:  How many lines of context to show

		- **returns**

			- `(list)`:  The formated code with context

	!!! abstract "method: `next(self)`"

		Read next character from the stream

		- **returns**

			- `(str)`:  the next character

	!!! abstract "method: `readline(self)`"

		Read a single line from the stream

		- **returns**

			- `(str)`:  the next line

	!!! abstract "method: `rewind(self)`"

		Rewind the stream

	!!! abstract "method: `split(self, delimiter, limit, trim, wraps, quotes, escape)`"

		Split the string of the stream

		- **params**

			- `delimiter (str)`:  The delimiter

			- `limit (int)`:  The max limit of the split

			- `trim (bool)`:  Whether to trim each part or not

			- `wraps (list)`:  A list of paired wraps to skip of                 the delimiter is wrapped by them

			- `quotes (str)`:  A series of quotes to skip of                 the delimiter is wrapped by them

			- `escape (str)`:  The escape character to see                 if any character is escaped

		- **returns**

			- `(list)`:  The split strings

	!!! abstract "method: `until(self, words, greedy, wraps, quotes, escape)`"

		Get the string until certain words
		For example:
		```
		s = LiquidStream.from_string("abcdefgh")
		s.until(["f", "fg"]) == "abcde", "fg"
		# cursor point to 'h'
		s.until(["f", "fg"], greedy = False) == "abcde", "f"
		# cursor point to 'g'
		s.until(["x", "xy"]) == "abcdefg", ""
		# cursor point to eos
		```

		- **params**

			- `words (list)`:  A list of words to search

			- `greedy (bool)`:  Whether do a greedy search or not

			    - Only effective when the words have prefices in common.                     For example

			    - ['abc', 'ab'], then abc will be matched first

			- `wraps (list)`:  A list of paired wraps to skip of the delimiter                 is wrapped by them

			- `quotes (str)`:  A series of quotes to skip of the delimiter is                 wrapped by them

			- `escape (str)`:  The escape character to see                 if any character is escaped

		- **returns**

			- `(str, str)`:  The string that has been searched and the matched word
## liquid.config


- **desc**

	Configurations for a Liquid object

!!! example "class: `LiquidConfig`"

	Configurations for a Liquid object
	

	- **params**

		- `mode (str)`:  The mode for `liquidpy` to handle the spaces

		    arround open tags

		- `loglevel (int|str)`:  The loglevel. Could be int identified

		    by `logging` module or `detail/15` defined in `liquidpy`

		- `include (str)`:  Paths to scan the included files

		    - multiple paths separated by `;`

		- `extends (str)`:  Paths to scan mother templates to extend.

		    - multiple paths separated by `;`

	!!! abstract "method: `tear(*args, **kwds)`"

		Leave a copy of config, when return,
		get the loglevel of LOGGER back

		- **yields**

			- `(LiquidConfig)`:  The new config object
