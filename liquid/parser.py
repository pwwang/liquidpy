"""
The parser for liquidpy
"""
import logging
from pathlib import Path
from .stream import LiquidStream
from .exceptions import LiquidSyntaxError
from .defaults import LIQUID_DEFAULT_MODE, LIQUID_COMPACT_TAGS, LIQUID_PAIRED_TAGS, \
	LIQUID_OPEN_TAGS, LIQUID_LOGGER_NAME, LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT, \
	LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT, LIQUID_STATE_OPENTAG, \
	LIQUID_STATE_OPENTAG_COMPACT, LIQUID_STATE_CLOSETAG, LIQUID_STATE_CLOSETAG_COMPACT, \
	LIQUID_MAX_STACKS, LIQUID_DEBUG_SOURCE_CONTEXT, LIQUID_TEXT_FILENAME

LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)

def _shorten(string, length = 15):
	"""Shorten a string used in debug information"""
	string = repr(string)[1:-1]
	if len(string) < length:
		return string
	remain = int(length / 2 - 5)
	return string[:remain] + ' ... ' + string[-remain:]

class LiquidLine:
	"""
	Line of compiled code
	"""
	__slots__ = ('line', 'lineno', 'parser', 'ndent')

	def __init__(self, line, parser = None, indent = 0):
		"""
		Constructor of line
		@params:
			`line`  : The compiled line
			`indent`: Number of indent of the line
		"""
		self.line   = line
		self.lineno = parser.lineno if parser else 0
		self.parser = parser
		self.ndent  = indent

	def __repr__(self):
		"""Get the repr of the object"""
		return '<LiquidLine {!r} (compiled from #{!r})>'.format(self.line,
			self.lineno if not self.parser else '{}:L{}'.format(self.parser.filename, self.lineno))

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

	def add_line(self, line, parser = None):
		"""
		Add a line of source to the code.
		Indentation and newline will be added for you, don't provide them.
		@params:
			line (str): The line to add
		"""
		if not isinstance(line, LiquidLine):
			line = LiquidLine(line, parser)
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

class LiquidParser: # pylint: disable=too-many-instance-attributes
	"""
	The parser class for liquidpy
	"""

	def __init__(self, stream, precode, code, filename, prev = None, baselineno = 1):
		"""
		Initialize the parser
		@params:
			stream (LiquidStream): The stream of the template
			precode (LiquidCode): The precode object
			code (LiquidCode): The main code object
		"""
		from . import nodes as liquid_nodes
		self.stream     = stream or LiquidStream.from_file(filename)
		self.filename   = filename
		self.nstacks    = prev[1].nstacks + 1 if prev else 1
		self.prev       = prev
		self.baselineno = baselineno
		self.lineno     = baselineno
		# if I have extends, I should just save the blocks
		# otherwise, I should use the blocks from prev parser and parse it
		self.extends  = None
		if self.nstacks >= LIQUID_MAX_STACKS:
			self.raise_ex('Max {} stacks reached'.format(self.nstacks))

		self.mode    = LIQUID_DEFAULT_MODE
		self.stack   = []
		self.history = []
		self.precode = precode
		self.code    = code
		self.blocks  = {}
		self.endtag  = None # previous closing tag
		self.nodes   = {name[4:].lower(): getattr(liquid_nodes, name)(self)
			for name in dir(liquid_nodes) if name.startswith('Node')}

	def raise_ex(self, msg):
		"""
		Raise the exception according to the debug level
		@params:
			msg (str): The error message
		"""
		if LOGGER.level < 20:
			raise LiquidSyntaxError(msg, self) from None
		raise LiquidSyntaxError(msg, self.lineno) from None

	def get_stacks(self, lineno = None):
		"""
		Get template call stacks
		@params:
			lineno (int): Current line number
		@returns:
			list: The formated stacks
		"""
		stacks = [(lineno or self.lineno, self)]
		prev   = self.prev
		while prev:
			stacks.insert(0, prev)
			prev = prev[1].prev

		ret = []
		for lno, parser in stacks:
			ret.append('File {}'.format(parser.filename))
			ret.extend('  ' + line for line in parser.stream.get_context(
				lno, LIQUID_DEBUG_SOURCE_CONTEXT if parser is self else 0, parser.baselineno))
		return ret

	def parse(self, first = True):
		"""
		Parse the template
		"""
		if first:
			LOGGER.debug("%s parsing file: %s",
				'START' if self.stream.cursor == 0 else 'CONTINUE', self.filename)
		string, tag = self.stream.until(LIQUID_OPEN_TAGS, wraps = [], quotes = [])

		if self.extends and tag and tag not in (LIQUID_STATE_OPENTAG, LIQUID_STATE_OPENTAG_COMPACT):
			self.lineno += string.count('\n')
			self.raise_ex("Only blocks allowed in template extending others")
		self.parse_literal(string, tag)
		self.lineno += string.count('\n')
		if tag in (LIQUID_EXPR_OPENTAG, LIQUID_EXPR_OPENTAG_COMPACT):
			self.parse_expression(tag)
			self.parse(False)
		elif tag in (LIQUID_COMMENT_OPENTAG, LIQUID_COMMENT_OPENTAG_COMPACT):
			self.parse_comment(tag)
			self.parse(False)
		elif tag in (LIQUID_STATE_OPENTAG, LIQUID_STATE_OPENTAG_COMPACT):
			file_switched = self.parse_statement(tag)
			self.parse(file_switched)
		self.lineno += string.count('\n')
		if self.stack:
			self.raise_ex('Statement {!r} not closed in {!r}'.format(
				self.stack[-1], self.filename))

		if self.extends:
			self.extends.parse()

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
			self.lineno += nodestr.count("\n")
			if not closetag:
				self.raise_ex('Expecting a closing tag for {!r}'.format(tag))
			nodestr = nodestr.strip()
			if not nodestr:
				self.raise_ex('Empty node')
			self.endtag = closetag
			return nodestr

	def _expect_end_state(self, tag, name, rest = ''): # pylint: disable=too-many-locals
		"""
		Get possible ending tags, like '{% endraw %}', '{%-endraw-%}'
		Only one space allowed
		"""
		opentags  = LIQUID_STATE_OPENTAG,  LIQUID_STATE_OPENTAG_COMPACT
		closetags = LIQUID_STATE_CLOSETAG, LIQUID_STATE_CLOSETAG_COMPACT
		endstates = []
		for opentag in opentags:
			for closetag in closetags:
				for openspace in ('', ' '):
					for closespace in ('', ' '):
						endstates.append(opentag + openspace + 'end' + name + closespace + closetag)
		string, endstate = self.stream.until(endstates)
		if not endstate:
			self.raise_ex('Expecting an end statement for {!r}'.format(name))
		# For blocks
		# we have to check if there are blocks in blocks, if so,
		# {% block a %} {% block b %} {% endblock %} {% endblock %}
		# The first endblock will be matched
		if name == 'block':
			nblocks = 0
			sstream = LiquidStream.from_string(string)
			_, opentag = sstream.until(opentags, wraps = [], quotes = [])
			while opentag:
				nodestr, closetag = sstream.until(closetags)
				if not closetag:
					break
				if nodestr.strip().split(maxsplit = 1)[0] == name:
					nblocks += 1
				_, opentag = sstream.until(opentags, wraps = [], quotes = [])

			for _ in range(nblocks):
				stringx, endstatex = self.stream.until(endstates)
				string += endstate + stringx
				endstate = endstatex

		LOGGER.debug("- Statement found at line %s: %s %s %s %s %s %s",
			self.lineno, tag, name, rest, self.endtag, _shorten(string), endstate)

		nlines = string.count("\n")
		leading_lines = 0 # to correct block line numbers
		if self.endtag in LIQUID_COMPACT_TAGS or self.mode == 'compact':
			string = string.lstrip(' \t')
			string2 = string.lstrip('\n')
			leading_lines = len(string) - len(string2)
			string = string2
		if endstate.startswith(LIQUID_STATE_OPENTAG_COMPACT) or self.mode == 'compact':
			string = string.rstrip(' \t').rstrip('\n')
		self.endtag = LIQUID_STATE_CLOSETAG_COMPACT if endstate.endswith(
			LIQUID_STATE_CLOSETAG_COMPACT) else LIQUID_STATE_CLOSETAG
		return string, nlines, leading_lines

	def parse_comment(self, tag):
		"""
		Parse the comment tag `{##}` or `{#--#}`
		@params:
			tag (str): The open tag.
		"""
		nodestr = self._expect_closing_tag(tag)
		nodestr = LiquidParser._multi_line_support(nodestr)
		LOGGER.debug("- Comment tag found at line %s: %s %s %s",
			self.lineno, tag, _shorten(nodestr), self.endtag)

	def parse_literal(self, string, tag):
		"""
		Parse the literal texts
		@params:
			string (str): The literal text
			tag (str): The end tag
		"""
		if not string:
			return
		LOGGER.debug("- Literals wrapped by tags (%s, %s) found at line %s: %r",
			self.endtag, tag, self.lineno, _shorten(string))
		if self.endtag in LIQUID_COMPACT_TAGS or self.mode == 'compact':
			string = string.lstrip(' \t').lstrip('\n')
		if tag in LIQUID_COMPACT_TAGS or self.mode == 'compact':
			string = string.rstrip(' \t').rstrip('\n')
		self.nodes['literal'].start(string)

	def parse_expression(self, tag):
		"""
		Parse the expressions like `{{ 1 }}`
		@params:
			tag (str): The open tag
		"""
		nodestr = self._expect_closing_tag(tag)
		nodestr = LiquidParser._multi_line_support(nodestr)
		LOGGER.debug("- Expression found at line %s: %s %s %s",
			self.lineno, tag, nodestr, self.endtag)
		self.nodes['expression'].start(nodestr)

	def parse_raw(self, tag):
		"""
		Parse the raw node
		@params:
			tag (str): The open tag
		"""
		string, nlines, _ = self._expect_end_state(tag, 'raw')
		self.nodes['raw'].start(string)
		self.lineno += nlines

	def parse_statement(self, tag):
		"""
		Parse the statement node
		@params:
			tag (str): The open tag
		"""
		nodestr = self._expect_closing_tag(tag)
		nodestr = LiquidParser._multi_line_support(nodestr)
		try:
			name, rest = nodestr.split(maxsplit = 1)
		except ValueError:
			name, rest = nodestr, ''

		if self.extends and name != 'block':
			self.raise_ex('Only blocks allowed in template extending others.')

		if nodestr == 'raw':
			self.parse_raw(tag)
			return False

		if name == 'block':
			self.parse_block(tag, rest)
			return False

		if name == 'extends':
			self.parse_extends(rest)
			return False

		if name == 'include':
			self.parse_include(rest)
			return True

		# else:
		if not rest and name[-1] == ':':
			name = name[:-1]

		LOGGER.debug("- Statement found at line %s: %s %s %s",
			self.lineno, tag, nodestr, self.endtag)
		end = name.startswith('end')
		name = name[3:] if end else name
		if name not in self.nodes:
			self.raise_ex('Unknown statement: {!r}'.format('end' + name if end else name))
		if end:
			if rest:
				self.raise_ex("Additional expression for 'end{}'".format(name))
			self.nodes[name].end()
		else:
			self.nodes[name].start(rest)
		return False

	def parse_block(self, tag, name):
		"""Parse a block"""
		if not name:
			self.raise_ex('Expecting a block name')
		block, nlines, leading_lines = self._expect_end_state(tag, 'block', name)
		self.history.append('block')

		if self.extends:
			LOGGER.debug("- Save blocks for replacing parent ones")
			self.blocks[name] = LiquidParser(LiquidStream.from_string(block),
				self.precode, self.code, self.filename, self.prev, self.lineno + leading_lines)
			self.blocks[name].mode = self.mode
			self.lineno += nlines
		# I am the parent
		elif self.prev and name in self.prev[1].blocks:
			LOGGER.debug("START parsing block %r from file: %s", name, self.prev[1].filename)
			self.prev[1].blocks[name].parse()
		else:
			LOGGER.debug("- Didn't find any blocks to replace, parsing block: %s", name)
			liqblock = LiquidParser(LiquidStream.from_string(block),
				self.precode, self.code, self.filename, self.prev, self.lineno + leading_lines)
			liqblock.mode = self.mode
			liqblock.parse(False)
			self.lineno += nlines

	def parse_extends(self, path):
		"""Parse a extends statement"""
		# make sure "extends" is the first node or after "mode"
		for hist in self.history:
			if hist != 'mode':
				self.raise_ex("Statement 'extends' should be place at the top or after 'mode'")
		extpath = Path(path.strip('\'"'))
		if not extpath.is_absolute():
			if self.filename != LIQUID_TEXT_FILENAME:
				extpath = Path(self.filename).parent.joinpath(path)
		if not extpath.is_file():
			self.raise_ex("Parent template does not exist: {!r}".format(path))
		self.history.append('extends')
		LOGGER.debug("- Extends found at line %s: %s", self.lineno, path)
		self.extends = LiquidParser(
			None, self.precode, self.code, extpath, prev = (self.lineno, self))

	def parse_include(self, path):
		"""Parse a include statement"""
		incpath = Path(path.strip('\'"'))
		if not incpath.is_absolute():
			if self.filename != LIQUID_TEXT_FILENAME:
				incpath = Path(self.filename).parent.joinpath(path)
		if not incpath.is_file():
			self.raise_ex("Template file does not exist: {!r}".format(path))
		self.history.append('include')
		LOGGER.debug("- Include found at line %s: %s", self.lineno, path)
		include = LiquidParser(None, self.precode, self.code, incpath, prev = (self.lineno, self))
		# allow imperfect matches
		include.stack = self.stack
		include.mode = self.mode
		include.parse()
