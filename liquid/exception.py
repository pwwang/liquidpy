
class LiquidSyntaxError(Exception):
	
	def __init__(self, msg, lineno = 0, src = ''):
		if lineno:
			super(LiquidSyntaxError, self).__init__("{} at line {}: {}".format(msg, lineno, src))
		else:
			super(LiquidSyntaxError, self).__init__(msg)

class LiquidRenderError(Exception):
	def __init__(self, exc, msg):
		super(LiquidRenderError, self).__init__("{}, {}".format(exc, msg))