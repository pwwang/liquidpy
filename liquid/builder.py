
class LiquidLine(object):
	"""
	Line of compiled code
	"""
	
	def __init__(self, line, lineno = 0, src = '', indent = 0):
		"""
		Constructor of line
		@params:
			`line`  : The compiled line
			`src`   : The source of the line
			`indent`: Number of indent of the line 
		"""
		self.line   = line
		self.src    = src or line
		self.lineno = lineno
		self.ndent  = indent

	def __repr__(self):
		"""
		For exceptions
		"""
		if self.lineno:
			return "at line {}: {}".format(self.lineno, self.src)
		else:
			return "in compiled source: {}".format(self.src)
	
	def __str__(self):
		return "{}{}\n".format("\t" * self.ndent, self.line)

class LiquidCode(object):
	"""
	Build source code conveniently.
	"""

	INDENT_STEP = 1

	def __init__(self, indent = 0):
		"""
		Constructor of code builder
		@params:
			`envs`  : The envs to compile the template
			`indent`: The initial indent level
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

	def addLine(self, line):
		"""
		Add a line of source to the code.
		Indentation and newline will be added for you, don't provide them.
		@params:
			`line`: The line to add
		"""
		if not isinstance(line, LiquidLine):
			line = LiquidLine(line)
		line.ndent = self.ndent
		self.codes.append(line)
	
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



