"""
The parser for liquidpy
"""
import logging
from .exceptions import LiquidSyntaxError
from .defaults import LIQUID_DEFAULT_MODE, LIQUID_COMPACT_TAGS, LIQUID_PAIRED_TAGS, \
	LIQUID_OPEN_TAGS, LIQUID_LOGGER_NAME, LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT, \
	LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT, LIQUID_STATE_OPENTAG, \
	LIQUID_STATE_OPENTAG_COMPACT, LIQUID_STATE_CLOSETAG, LIQUID_STATE_CLOSETAG_COMPACT

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

class LiquidLine:
	"""
	Line of compiled code
	"""

	def __init__(self, line, lineno = 0, indent = 0):
		"""
		Constructor of line
		@params:
			`line`  : The compiled line
			`src`   : The source of the line
			`indent`: Number of indent of the line
		"""
		self.line   = line
		self.lineno = lineno
		self.ndent  = indent

	def __repr__(self):
		"""Get the repr of the object"""
		return '<LiquidLine {!r} (compiled from #{!r})>'.format(self.line, self.lineno)

	def __str__(self):
		"""Stringify the object"""
		return "{}{}\n".format(" " * 2 * self.ndent, self.line)

class LiquidCode:
	"""
	Build source code conveniently.
	"""

	INDENT_STEP = 1

	def __init__(self, indent = 0):
		"""
		Constructor of code builder
		@params:
			indent (int): The initial indent level
		"""
		self.codes = []
		self.ndent = indent

	def __str__(self):
		"""
		Concatnate of the codes
		@returns:
			The concatnated string
		"""
		return "".join(str(c) for c in self.codes)

	def add_line(self, line, lineno = 0):
		"""
		Add a line of source to the code.
		Indentation and newline will be added for you, don't provide them.
		@params:
			line (str): The line to add
		"""
		if not isinstance(line, LiquidLine):
			line = LiquidLine(line, lineno)
		line.ndent = self.ndent
		self.codes.append(line)

	def add_code(self, code):
		"""
		Add a LiquidCode object to the code.
		Indentation and newline will be added for you, don't provide them.
		@params:
			code (LiquidCode): The LiquidCode object to add
		"""
		assert isinstance(code, LiquidCode)
		code.ndent += self.ndent
		self.codes.extend(code.codes)

	def indent(self):
		"""
		Increase the current indent for following lines.
		"""
		self.ndent += self.INDENT_STEP

	def dedent(self):
		"""
		Decrease the current indent for following lines.
		"""
		self.ndent -= self.INDENT_STEP

class LiquidParser:
	"""
	The parser class for liquidpy
	"""

	def __init__(self, stream, precode, code):
		"""
		Initialize the parser
		@params:
			stream (Stream): The stream of the template
			precode (LiquidCode): The precode object
			code (LiquidCode): The main code object
		"""
		from . import nodes as liquid_nodes
		self.stream    = stream
		self.meta      = {
			'mode'    : LIQUID_DEFAULT_MODE,
			'stack'   : [],
			'precode' : precode,
			'code'    : code,
			'raise'   : self.raise_ex
		}
		self.lineno = 1
		self.endtag = None # previous closing tag
		self.nodes  = {name[4:].lower(): getattr(liquid_nodes, name)(self.meta)
			for name in dir(liquid_nodes) if name.startswith('Node')}

	def raise_ex(self, msg):
		"""
		Raise the exception according to the debug level
		@params:
			msg (str): The error message
		"""
		if LOGGER.level < 20:
			raise LiquidSyntaxError(msg, self.lineno, self.stream) from None
		raise LiquidSyntaxError(msg, self.lineno) from None

	def parse(self):
		"""
		Parse the template
		"""
		string, tag = self.stream.until(LIQUID_OPEN_TAGS, wraps = [], quotes = [])

		self.parse_literal(string, tag)
		self.lineno += string.count('\n')
		if tag in (LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT):
			self.parse_expression(tag)
			self.parse()
		elif tag in (LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT):
			self.parse_comment(tag)
			self.parse()
		elif tag in (LIQUID_STATE_OPENTAG, LIQUID_STATE_OPENTAG_COMPACT):
			self.parse_statement(tag)
			self.parse()
		self.lineno += string.count('\n')
		if self.meta['stack']:
			self.raise_ex('Statement {!r} not closed'.format(self.meta['stack'][-1]))

	@staticmethod
	def _multi_line_support(string):
		"""
		Support multi-line statements, comments (tag) and expressions
		Turn this:
		```
		assign a = xyz | filter1
		               | filter2
		```
		to:
		```
		assign a = xyz | filter1 | filter2
		```
		"""
		lines = string.splitlines()
		lens  = len(lines)
		lines = (line.rstrip() if i == 0 else line.lstrip() if i == lens - 1 else line.strip()
				  for i, line in enumerate(lines))
		return ' '.join(lines)

	def _expect_closing_tag(self, tag):
		"""
		Get the closing tag of an open one
		@params:
			tag (str): The open tag
		@returns:
			The content of the node.
			For example: `abc` of `{% abc %}`. `%}` will be saved in `self.endtag`
		"""
		for ptags in LIQUID_PAIRED_TAGS:
			if tag not in ptags[0]:
				continue
			nodestr, closetag = self.stream.until(ptags[1])
			if not closetag:
				self.raise_ex('Expecting a closing tag for {!r}'.format(tag))
			nodestr = nodestr.strip()
			if not nodestr:
				self.raise_ex('Empty node')
			self.endtag = closetag
			return nodestr

	def parse_comment(self, tag):
		"""
		Parse the comment tag `{##}` or `{#--#}`
		@params:
			tag (str): The open tag.
		"""
		nodestr = self._expect_closing_tag(tag)
		nodestr = LiquidParser._multi_line_support(nodestr)
		LOGGER.debug("Comment tag found at line %s: %s %s %s",
			self.lineno, tag,
			nodestr if len(nodestr) < 14 else nodestr[:5] + ' ... ' + nodestr[:-5], self.endtag)

	def parse_literal(self, string, tag):
		"""
		Parse the literal texts
		@params:
			string (str): The literal text
			tag (str): The end tag
		"""
		if not string:
			return
		LOGGER.debug("Literals wrapped by tags [%r, %r] found at line %s: %r",
			self.endtag, tag, self.lineno,
			string if len(string) < 13 else string[:5] + ' ... ' + string[:-5])
		if self.endtag in LIQUID_COMPACT_TAGS or self.meta['mode'] == 'compact':
			string = string.lstrip(' \t').lstrip('\n')
		if tag in LIQUID_COMPACT_TAGS or self.meta['mode'] == 'compact':
			string = string.rstrip(' \t').rstrip('\n')
		self.nodes['literal'].start(string, self.lineno)

	def parse_expression(self, tag):
		"""
		Parse the expressions like `{{ 1 }}`
		@params:
			tag (str): The open tag
		"""
		nodestr = self._expect_closing_tag(tag)
		nodestr = LiquidParser._multi_line_support(nodestr)
		LOGGER.debug("Expression found at line %s: %s %s %s",
			self.lineno, tag, nodestr, self.endtag)
		self.nodes['expression'].start(nodestr, self.lineno)

	def parse_raw(self, tag, endtag):
		"""
		Parse the raw node
		@params:
			tag (str): The open tag
			endtag (str): The end tag
		"""
		opentags  = LIQUID_STATE_OPENTAG,  LIQUID_STATE_OPENTAG_COMPACT
		closetags = LIQUID_STATE_CLOSETAG, LIQUID_STATE_CLOSETAG_COMPACT
		endraws   = []
		for opentag in opentags:
			for closetag in closetags:
				for openspace in ('', ' '):
					for closespace in ('', ' '):
						endraws.append(opentag + openspace + 'endraw' + closespace + closetag)

		string, endraw = self.stream.until(endraws)
		if not endraw:
			self.raise_ex("Expecting closing a tag for 'raw'")

		LOGGER.debug("Statement found at line %s: %s raw %s %s %s",
			self.lineno, tag, endtag,
			string if len(string) < 14 else string[:5] + ' ... ' + string[:-5], endraw)
		if endtag in LIQUID_COMPACT_TAGS or self.meta['mode'] == 'compact':
			string = string.lstrip(' \t').lstrip('\n')
		if endraw.startswith(LIQUID_STATE_OPENTAG_COMPACT) or self.meta['mode'] == 'compact':
			string = string.rstrip(' \t').rstrip('\n')

		self.endtag = LIQUID_STATE_CLOSETAG_COMPACT if endraw.endswith(
			LIQUID_STATE_CLOSETAG_COMPACT) else LIQUID_STATE_CLOSETAG
		self.lineno += string.count('\n')

		self.nodes['raw'].start(string, self.lineno)

	def parse_statement(self, tag):
		"""
		Parse the statement node
		@params:
			tag (str): The open tag
		"""
		nodestr = self._expect_closing_tag(tag)
		if nodestr == 'raw':
			self.parse_raw(tag, self.endtag)
			return

		nodestr = LiquidParser._multi_line_support(nodestr)
		try:
			name, rest = nodestr.split(maxsplit = 1)
		except ValueError:
			name, rest = nodestr, ''
		# else:
		if not rest and name[-1] == ':':
			name = name[:-1]

		LOGGER.debug("Statement found at line %s: %s %s %s", self.lineno, tag, nodestr, self.endtag)
		end = name.startswith('end')
		name = name[3:] if end else name
		if name not in self.nodes:
			self.raise_ex('Unknown statement: {!r}'.format('end' + name if end else name))
		if end:
			if rest:
				self.raise_ex("Additional expression for 'end{}'".format(name))
			self.nodes[name].end()
		else:
			self.nodes[name].start(rest, self.lineno)
