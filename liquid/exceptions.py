"""
Exceptions used in liquidpy
"""

import math
from .defaults import LIQUID_DEBUG_SOURCE_CONTEXT

def _show_source_context(source, lineno, context):
	"""
	Show the line of source code and its context
	@params:
		source (list): The whole source code
		lineno (int): Line number of current line
		context (int): How many lines of context to show
	@returns:
		The formated code with context
	"""
	ret = []
	maxline = lineno + context
	nbit = math.ceil(math.log(maxline + 1, 10))
	for i, line in enumerate(source):
		line = str(line).rstrip()
		if i+1 < lineno - context or i+1 > maxline:
			continue
		if i+1 == lineno:
			ret.append("> {}. {}".format(str(i+1).rjust(nbit), line))
		else:
			ret.append("  {}. {}".format(str(i+1).rjust(nbit), line))
	return ret

class LiquidSyntaxError(Exception):
	"""Raises when there is a syntax error in the template"""

	def __init__(self, msg, lineno = 0, stream = None):
		"""
		Initialize the exception
		@params:
			msg (str): The error message
			lineno (int): The line number of current source code
			stream (Stream): Stream of the whole source code
		"""
		if stream:
			msg = [	"{} at line {}".format(msg, lineno),
					"",
					"Template source (turn debug off to hide this):",
					"--------------------------------------------"]
			cursor = stream.stream.tell()
			stream.rewind()
			msg.extend(_show_source_context(
				stream.stream.readlines(), lineno, LIQUID_DEBUG_SOURCE_CONTEXT))
			stream.stream.seek(cursor)
			msg = "\n".join(msg)
		elif lineno:
			msg = "{} at line {}".format(msg, lineno)
		super().__init__(msg)

class LiquidRenderError(Exception):
	"""Raises when the template fails to render"""
	def __init__(self, exc, msg = ''):
		"""Initialize the exception
		@params:
			exc (Exception): The original exception
			msg (str): The error message
		"""
		super(LiquidRenderError, self).__init__("{}{}".format(exc, ', ' + msg if msg else ''))

class LiquidWrongKeyWord(Exception):
	"""Raises when the key of the environment or context is invalid"""
