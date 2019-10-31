"""
Exceptions used in liquidpy
"""
class LiquidSyntaxError(Exception):
	"""Raises when there is a syntax error in the template"""

	def __init__(self, msg, parser = 0):
		"""
		Initialize the exception
		@params:
			msg (str): The error message
			parser (LiquidParser): The parser
		"""
		if isinstance(parser, int):
			msg = "{} at line {}".format(msg, parser)
		elif parser:
			msg = [msg, '']
			msg.append('Template call stacks:')
			msg.append('----------------------------------------------')
			msg.extend(parser.get_stacks())
			msg = "\n".join(msg)
		super().__init__(msg)

class LiquidRenderError(Exception):
	"""Raises when the template fails to render"""

class LiquidWrongKeyWord(Exception):
	"""Raises when the key of the environment or context is invalid"""
