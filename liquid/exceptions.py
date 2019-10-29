
import math
from .defaults import LIQUID_DEBUG_SOURCE_CONTEXT

def _show_source_context(source, lineno, context):
	ret = []
	maxline = lineno + context
	nbit = math.ceil(math.log(maxline + 1, 10))
	for i, line in enumerate(source):
		line = str(line).rstrip()
		if i+1 < lineno - context or i+1 > maxline:
			continue
		if i+1 == lineno:
			ret.append("> {}. {}".format(str(i+1).ljust(nbit), line))
		else:
			ret.append("  {}. {}".format(str(i+1).ljust(nbit), line))
	return ret

class LiquidSyntaxError(Exception):

	def __init__(self, msg, lineno = 0, stream = None):
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
	def __init__(self, exc, msg = ''):

		super(LiquidRenderError, self).__init__("{}{}".format(exc, ', ' + msg if msg else ''))

class LiquidWrongKeyWord(Exception):
	pass