
class LiquidSyntaxError(Exception):
	
	def __init__(self, msg, lineno = 0, src = ''):
		super(LiquidSyntaxError, self).__init__("{} at line {}: {}".format(msg, lineno, src))