"""
Liquid template engine for python
"""
__version__ = "0.1.0"

import logging
import keyword
from .stream import Stream
from .parser import LiquidLine, LiquidCode, LiquidParser
from .exceptions import LiquidSyntaxError, LiquidRenderError, LiquidWrongKeyWord, \
	_show_source_context
from .filters import LIQUID_FILTERS, PYTHON_FILTERS
from .defaults import LIQUID_LOGGER_NAME, LIQUID_DEFAULT_ENVS, LIQUID_RENDER_FUNC_NAME, \
	LIQUID_COMPILED_RENDERED, LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RR_EXTEND, \
	LIQUID_COMPILED_CONTEXT, LIQUID_SOURCE_NAME, LIQUID_DEBUG_SOURCE_CONTEXT, \
	LIQUID_LIQUID_FILTERS

logging.basicConfig(
	level  = logging.INFO,
	format = '[%(asctime)-15s %(levelname)5s] %(message)s')
LOGGER = logging.getLogger(LIQUID_LOGGER_NAME)


def _check_envs(envs, additional = None):
	"""
	Check the keys of environment. Because we are using the keys as variable name in the template,
	so we have to make sure they are valid.
	@params:
		additional (list): A list of additional keys to check.
	@returns:
		`True` if passed else `False`
	"""
	additional = additional or []
	for kword in envs:
		if not kword or not kword.strip():
			raise LiquidWrongKeyWord('Empty string cannot be used as variable name.')
		if kword in LIQUID_DEFAULT_ENVS:
			raise LiquidWrongKeyWord('"{}" cannot be used as variable name, as'
				'it is bound to value {!r}'.format(kword, LIQUID_DEFAULT_ENVS[kword]))
		if kword in keyword.kwlist:
			raise LiquidWrongKeyWord('"{}" cannot be used as variable name, as'
				'it is a python language keyword.'.format(kword))
		if kword in (*additional, LIQUID_RENDER_FUNC_NAME,
			LIQUID_COMPILED_RENDERED, LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RR_EXTEND,
			LIQUID_LIQUID_FILTERS):
			raise LiquidWrongKeyWord('"{}" cannot be used as variable name, as'
			'it is a liquidpy keyword.'.format(kword))

class Liquid:

	"""The main class"""

	@staticmethod
	def debug(dbg = None):
		"""
		Set or get the debug mode
		@params:
			dbg: `None` to return if now we are in debug mode
				- True/False to turn on/off the debug mode
		@returns:
			Return the current debug mode when `dbg` is `None`
		"""
		if dbg is None:
			return LOGGER.level <= logging.DEBUG
		if dbg:
			LOGGER.setLevel(logging.DEBUG)
		else:
			LOGGER.setLevel(logging.INFO)
		return None

	def __init__(self, text = '', **envs):
		"""
		Initialize a liquid object
		@params:
			text (str): The template string
			**envs (kwargs): The environment.
				- If `from_file` provided, use it as the template
		"""
		if 'from_file' in envs and text:
			raise ValueError('Cannot have both "text" and "from_file" specified, '
				'choose either one.')

		self.stream = Stream.from_string(text) if text else \
			Stream.from_file(envs.pop('from_file'))
		_check_envs(envs)
		self.envs   = LIQUID_DEFAULT_ENVS.copy()
		self.envs.update(envs)
		self.envs.update(PYTHON_FILTERS)
		self.envs[LIQUID_LIQUID_FILTERS] = LIQUID_FILTERS

		self.precode  = LiquidCode()
		self.code     = LiquidCode()
		self.code.indent()
		self.precode.indent()

		self.precode.add_line("{} = []".format(LIQUID_COMPILED_RENDERED))
		self.precode.add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
		self.precode.add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))

		LiquidParser(self.stream, self.precode, self.code).parse()
		self.code.add_line("return ''.join(str(x) for x in {})".format(LIQUID_COMPILED_RENDERED))

	def render(self, **context):
		"""
		Render the template
		@params:
			**context: The context for rendering.
		"""
		_check_envs(context)
		final_context = self.envs.copy()
		final_context.update(context)

		finalcode = LiquidCode()
		finalcode.add_line("def {}({}):".format(
			LIQUID_RENDER_FUNC_NAME, LIQUID_COMPILED_CONTEXT))
		finalcode.indent()
		# expand the variables from context
		for key in final_context:
			finalcode.add_line('{key} = {context}[{key!r}]'.format(
				key = key, context = LIQUID_COMPILED_CONTEXT))
		finalcode.add_code(self.precode)
		finalcode.add_code(self.code)
		strcode = str(finalcode)
		LOGGER.debug("The compiled code:\n%s", strcode)
		try:
			strcode = compile(strcode, LIQUID_SOURCE_NAME, 'exec')
			localns = {}
			exec(strcode, None, localns) # pylint: disable=exec-used
			return localns[LIQUID_RENDER_FUNC_NAME](final_context)
		except Exception:
			import traceback
			stacks = list(reversed(traceback.format_exc().splitlines()))
			stack_with_file = [stack.strip() for stack in stacks
				if stack.strip().startswith('File "{}"'.format(LIQUID_SOURCE_NAME))]
			stack  = stack_with_file[-1]
			lineno = int(stack.split(', ')[1].split()[-1])
			msg    = [stacks[0]]
			if 'NameError:' in stacks[0]:
				msg[0] += ', do you forget to provide the data for the variable?'
			msg.append('')
			msg.append('At source line {}:'.format(finalcode.codes[lineno-1].lineno))
			msg.append('----------------------------------------------')
			self.stream.rewind()
			msg.extend(_show_source_context(
				self.stream.stream.readlines(), finalcode.codes[lineno-1].lineno, 1))

			if not stack_with_file or not Liquid.debug(): # not at debug level
				raise LiquidRenderError('\n'.join(msg)) from None

			msg.append('')
			msg.append('Compiled source (turn debug off to hide this):')
			msg.append('----------------------------------------------')
			msg.extend(_show_source_context(
				finalcode.codes, lineno, LIQUID_DEBUG_SOURCE_CONTEXT))

			msg.append('')
			msg.append('Context:')
			msg.append('----------------------------------------------')
			for key, val in context.items():
				msg.append('  {}: {!r}'.format(key, val))

			raise LiquidRenderError('\n'.join(msg)) from None
