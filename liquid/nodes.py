"""
The nodes supported by liquidpy
"""
#pylint:disable=too-many-statements
import logging
from .stream import LiquidStream
from .filters import LIQUID_FILTERS
from .defaults import LIQUID_LOGGER_NAME, LIQUID_MODES, \
	LIQUID_LIQUID_FILTERS, LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RR_EXTEND, \
	LIQUID_COMPILED_RENDERED

def push_history(func):
	"""Push the node to the history"""
	def retfunc(self, *args, **kwargs):
		"""Push the tag in history and then do the stuff"""
		func(self, *args, **kwargs)
		self.parser.history.append(self.name)
	return retfunc

def push_both(func):
	"""Push the node to both stack and history"""
	def retfunc(self, *args, **kwargs):
		"""Push the tag in both stack and history and then do the stuff"""
		self.parser.stack.append(self.name)
		func(self, *args, **kwargs)
		self.parser.history.append(self.name)
	return retfunc

def pop_stack(func):
	"""Pop the node from the stack"""
	def retfunc(self, *args, **kwargs):
		"""Pop the tag in stack and then do the stuff"""
		last = self.parser.stack.pop() if self.parser.stack else None
		if last != self.name:
			if last:
				self.parser.raise_ex(
					"Unmatched end tag: 'end{}', expect 'end{}'".format(self.name, last))
			self.parser.raise_ex("Unmatched end tag: 'end{}'".format(self.name))
		func(self, *args, **kwargs)
	return retfunc

def dedent(func):
	"""Dedent the code"""
	def retfunc(self, *args, **kwargs):
		"""Do the stuff and dedent the code"""
		func(self, *args, **kwargs)
		self.parser.code.dedent()
	return retfunc

class _Node:
	"""The base class"""

	def __init__(self, parser):
		"""Initialize the node"""
		self.parser = parser
		self.name = self.__class__.__name__[4:].lower()

	def start(self, string):
		"""Start to compile the node"""

	@pop_stack
	@dedent
	def end(self):
		"""end node hit"""


class NodeMode(_Node):
	"""
	Node '{% mode ... %}'
	"""

	def _set_mode(self, mode):
		"""Set the mode"""
		if mode not in LIQUID_MODES:
			self.parser.raise_ex('Not a valid mode: {!r}'.format(mode))
		self.parser.mode = mode

	def _set_loglevel(self, loglevel):
		"""Set the loglevel"""
		loglevel = loglevel.upper()
		if not NodeMode._is_loglevel(loglevel):
			self.parser.raise_ex('Not a valid loglevel: {!r}'.format(loglevel))
		logging.getLogger(LIQUID_LOGGER_NAME).setLevel(loglevel)

	@staticmethod
	def _is_loglevel(loglevel):
		"""Tell if a string is a valid loglevel"""
		return isinstance(logging.getLevelName(loglevel), int)

	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not string:
			self.parser.raise_ex('Expecting a mode value')
		parts = string.split()
		if len(parts) == 1:
			parts = parts[0].split(',')
		parts  = [part.strip() for part in parts]
		if len(parts) > 2:
			self.parser.raise_ex('Mode can only take at most 2 values')

		if len(parts) == 1:
			if NodeMode._is_loglevel(parts[0].upper()):
				self._set_loglevel(parts[0])
			else:
				self._set_mode(parts[0])

		else:
			part1, part2 = parts[:2]
			if NodeMode._is_loglevel(part1.upper()):
				self._set_loglevel(part1)
				self._set_mode(part2)
			else:
				self._set_mode(part1)
				self._set_loglevel(part2)

class NodeIf(_Node):

	"""
	Node '{% if ... %} {% endif %}'
	"""
	@push_both
	def start(self, string, prefix = 'if ', suffix = ''): # pylint:disable=arguments-differ
		"""Start to compile the node"""
		if not string:
			self.parser.raise_ex('No expressions for statement "{}"'.format(self.name))
		sstream = LiquidStream.from_string(string)
		# merge multiple lines
		#sstream = LiquidStream.from_string(' '.join(sstream.split(['\\\n'])))
		prestr, bracket = sstream.until(['`'])
		ifexpr = prefix
		if not bracket:
			ifexpr += prestr
		while bracket:
			expr, endbrkt = sstream.until(['`'])

			if endbrkt:
				ifexpr += prestr + NodeExpression(self.parser)._parse(expr)
				prestr, bracket = sstream.until(['`'])
				if not bracket:
					ifexpr += prestr
			else: # pragma: no cover
				# this technically will not  happen
				# because if there is only on `, there should be a syntax error
				ifexpr += prestr + '`' + expr + endbrkt
				bracket = ''
		ifexpr = (ifexpr[:-1] if ifexpr[-1] == ':' else ifexpr) + suffix
		self.parser.code.add_line(ifexpr + ':', self.parser)
		self.parser.code.indent()

class NodeElse(_Node):

	"""
	Node '{% else/else if... %}'
	"""

	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not self.parser.stack or self.parser.stack[-1] not in ('case', 'if', 'unless'):
			self.parser.raise_ex('"else" must be in an if/unless/case statement')
		# see if it is else if
		parts = string.split(maxsplit = 1)
		if not parts:
			self.parser.code.dedent()
			self.parser.code.add_line('else:')
			self.parser.code.indent()
		elif parts[0] == 'if' and self.parser.stack[-1] == 'if':
			ifnode = NodeIf(self.parser)
			self.parser.code.dedent()
			ifnode.start(parts[1] if len(parts) > 1 else '', 'elif ')
			ifnode.end()
			self.parser.code.indent()
		else:
			self.parser.raise_ex('"else" should not be followed by any expressions')

class NodeElseif(_Node):
	"""
	Node '{% elseif ... %} '
	"""

	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not self.parser.stack or self.parser.stack[-1] != 'if':
			self.parser.raise_ex('"elseif/elif/elsif" must be in an "if/unless" statement')
		ifnode = NodeIf(self.parser)
		self.parser.code.dedent()
		ifnode.start(string, 'elif ')
		ifnode.end()
		self.parser.code.indent()

NodeElif = NodeElsif = NodeElseif

class NodeLiteral(_Node):
	"""
	Literal node
	"""
	def start(self, string):
		"""Start to compile the node"""
		if not string:
			return
		lines = string.splitlines(keepends = True)
		if len(lines) > 1:
			self.parser.code.add_line('{}(['.format(LIQUID_COMPILED_RR_EXTEND))
			self.parser.code.indent()
			for line in lines:
				self.parser.code.add_line('{!r},'.format(line), self.parser)
			self.parser.code.dedent()
			self.parser.code.add_line('])')
		else:
			self.parser.code.add_line('{}({!r})'.format(
				LIQUID_COMPILED_RR_APPEND, lines[0]), self.parser)

NodeRaw = NodeLiteral

class NodeExpression(_Node):
	"""
	Expression node
	"""
	LIQUID_DOT_FUNC_NAME = '_liquid_dodots_function'

	@staticmethod
	def _parse_base(expr, single = False):
		"""
		Parse the first part of an expression
		"""
		if single:
			dots = LiquidStream.from_string(expr).split('.')
			# in case we have a float number
			# 1.2 or 1.3e-10
			ret = dots.pop(0)
			if ret.isdigit() and dots and dots[0].isdigit():
				ret = ret + '.' + dots.pop(0)

			for dot in dots:
				dstream = LiquidStream.from_string(dot)
				dot, dim = dstream.until(['[', '('])
				if dim:
					dim = dim + dstream.dump()

				# dodots(a, 'b')[1]
				ret = '{}({}, {!r}){}'.format(NodeExpression.LIQUID_DOT_FUNC_NAME, ret, dot, dim or '')
			return ret
		# what about "(1,2), (3,4)", "((1,2), (3,4))", "(((1,2), (3,4)))", (((1,2)))
		# (((1))) and "((1,2), [3,4])"? ((((1,2), 3), (4,5)))
		# 1. remove redundant (): -> "(1,2), (3,4)", "(1,2), (3,4)", "(1,2), (3,4)", (1,2)
		#   (1) and "((1,2), [3,4])"? ((1,2), 3), (4,5)
		lenexpr  = len(expr)
		lbracket = lenexpr - len(expr.lstrip('('))
		rbracket = lenexpr - len(expr.rstrip(')'))
		minbrkt  = min(lbracket, rbracket)
		if minbrkt > 0:
			expr = '(' + expr[minbrkt:-minbrkt] + ')'

		parts = LiquidStream.from_string(expr).split(',')
		# if we can split, ok, we have removed all redundant ()
		if len(parts) > 1:
			return '({})'.format(', '.join(NodeExpression._parse_base(part, single = True)
				for part in parts))
		if minbrkt > 0:
			# if we cannot, like (1), (1,2), ((1,2), [3,4]), try to remove the bracket again ->
			#   "1", "1,2", "(1,2), [3,4]"
			parts = LiquidStream.from_string(expr[1:-1]).split(',')
			if len(parts) > 1:
				return '({})'.format(', '.join(NodeExpression._parse_base(part, single = True)
					for part in parts))
		return NodeExpression._parse_base(parts[0], single = True)

	def _get_modifiers(self, filt):
		"""Get the modifiers from a filter"""
		modifiers = {'?': False, '*': False, '@': False}
		while filt[0] in modifiers:
			if modifiers[filt[0]]:
				self.parser.raise_ex('Repeated modifier: {!r}'.format(filt[0]))
			modifiers[filt[0]] = True
			filt = filt[1:]
		return modifiers, filt

	def _parse_filter(self, expr, args, tenary_stack):
		"""Parse the following part of an expression
		1. {{a | .a.b.c}}
		2. {{a | .a.b: 1,2}}
		3. {{a | ['a'] }}
		4. {{a | ['a']: 1,2 }}
		5. {{a | .a['b']: 1,2}}
		6. {{a | filter: 1,2}}
		7. {{a | @liquid_filter: 1, _0, 2}}
		8. {{a | lambda x: x+1}}
		9. {{a | : _ + 1}}
		10.{{a, b | *min}}
		"""
		modifiers, expr = self._get_modifiers(expr)

		if modifiers['?'] and tenary_stack:
			self.parser.raise_ex(
				'Unnecessary modifier "?", expect filters for True/False conditions')
		elif modifiers['?']:
			tenary_stack.append('?')

		eparts    = LiquidStream.from_string(expr).split(':', limit = 1)
		base      = None
		argprefix = '*' if args[0] == '(' and args[-1] == ')' and modifiers['*'] else ''
		eparts[0] = eparts[0].lstrip('*@')
		eparts[0] = eparts[0] or 'lambda _'

		if eparts[0][0] in ('.', '['):
			if modifiers['*'] or modifiers['@']:
				self.parser.raise_ex('Attribute filter should not have modifiers')
			base = NodeExpression._parse_base(args + eparts[0], single = True)

		if modifiers['@'] and eparts[0] not in LIQUID_FILTERS:
			self.parser.raise_ex("Unknown liquid filter: '@{}'".format(eparts[0]))
		filter_name = '{}[{!r}]'.format(
			LIQUID_LIQUID_FILTERS, eparts[0]) if modifiers['@'] else eparts[0]

		if len(eparts) == 1:
			#      1, 3 or 10
			return base or '{}({})'.format(filter_name, argprefix + args)
		if base: # 2, 4, 5
			return '{}({})'.format(base, eparts[1])
		if eparts[0].startswith('lambda '): # 8, 9
			return '({}: ({}))({}{})'.format(eparts[0], eparts[1], argprefix, args)
		# 6, 7
		fastream = LiquidStream.from_string(eparts[1])
		faparts = fastream.split(',')
		faparts = ['_'] if len(faparts) == 1 and not faparts[0] else faparts

		found_args = False
		for i, fapart in enumerate(faparts):
			if fapart == '_':
				faparts[i] = argprefix + args
				found_args = True
			elif fapart[0] == '_' and fapart[1:].isdigit():
				faparts[i] = '{}[{}]'.format(args, fapart[1:])
				found_args = True
		if not found_args:
			faparts.insert(0, argprefix + args)
		return '{}({})'.format(filter_name, ', '.join(faparts))

	def _parse(self, string):
		"""Start to parse the node"""
		#if not string: # Empty node
		#	self.parser.raise_ex('Nothing found for expression')

		if 	not hasattr(self.parser.precode, NodeExpression.LIQUID_DOT_FUNC_NAME) or \
			not getattr(self.parser.precode, NodeExpression.LIQUID_DOT_FUNC_NAME):
			setattr(self.parser.precode, NodeExpression.LIQUID_DOT_FUNC_NAME, True)
			self.parser.precode.add_line('def {}(obj, dot):'.format(NodeExpression.LIQUID_DOT_FUNC_NAME))
			self.parser.precode.indent()
			self.parser.precode.add_line('try:')
			self.parser.precode.indent()
			self.parser.precode.add_line('return getattr(obj, dot)')
			self.parser.precode.dedent()
			self.parser.precode.add_line('except (AttributeError, TypeError):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return obj[dot]')
			self.parser.precode.dedent()
			self.parser.precode.dedent()
			self.parser.precode.add_line('')

		sstream      = LiquidStream.from_string(string)
		exprs        = sstream.split('|')
		value        = NodeExpression._parse_base(exprs[0])
		# tenary_stack: {{ x | ?bool | :"Yes" | :"No" }}
		# 0: ? The mark for the start of tenary filter
		# 1: x The base value
		# 2: bool(x) The condition
		# 3: lambda _: "Yes" The value for True
		# 4: lambda _: "No" The value for False
		tenary_stack = []
		for expr in exprs[1:]:
			if not expr:
				self.parser.raise_ex('No filter specified')
			if not tenary_stack:
				value2 = self._parse_filter(expr, value, tenary_stack)
				if tenary_stack:
					# {{ "" | ?bool | :"Yes" | :"No"}}
					# value == ""
					# value2 == 'bool("")'
					tenary_stack.append(value)
					tenary_stack.append(value2)
				value = value2
				continue
			value = self._parse_filter(expr, tenary_stack[1], tenary_stack)
			tenary_stack.append(value)
			if len(tenary_stack) == 5:
				value = '(({2}) if ({1}) else ({3}))'.format(*tenary_stack[1:])
				tenary_stack = []
		if tenary_stack:
			self.parser.raise_ex('Missing True/False actions for ternary filter')
		return value

	@push_history
	def start(self, string):
		"""Start to compile the node"""
		self.parser.code.add_line('{}({})'.format(
			LIQUID_COMPILED_RR_APPEND, self._parse(string)), self.parser)

class NodeFor(_Node):
	"""
	Node '{% for ... %} {% endfor %}'
	"""
	LIQUID_FORLOOP_CLASS = '_Liquid_forloop_class'

	@push_both
	def start(self, string):
		"""Start to compile the node"""
		# i, v in x | range

		if  not hasattr(self.parser.precode, NodeFor.LIQUID_FORLOOP_CLASS) or \
			not getattr(self.parser.precode, NodeFor.LIQUID_FORLOOP_CLASS):
			setattr(self.parser.precode, NodeFor.LIQUID_FORLOOP_CLASS, True)

			self.parser.precode.add_line('class {}:'.format(NodeFor.LIQUID_FORLOOP_CLASS))
			self.parser.precode.indent()
			self.parser.precode.add_line('def __init__(self, iterable):')
			self.parser.precode.indent()
			self.parser.precode.add_line('self._iterable = [it for it in iterable]')
			self.parser.precode.add_line('self.index0 = -1')
			self.parser.precode.add_line('self.length = len(self._iterable)')
			self.parser.precode.dedent()
			self.parser.precode.add_line('@property')
			self.parser.precode.add_line('def first(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self.index0 == 0')
			self.parser.precode.dedent()
			self.parser.precode.add_line('@property')
			self.parser.precode.add_line('def last(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self.index == self.length')
			self.parser.precode.dedent()
			self.parser.precode.add_line('@property')
			self.parser.precode.add_line('def index(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self.index0 + 1')
			self.parser.precode.dedent()
			self.parser.precode.add_line('@property')
			self.parser.precode.add_line('def rindex(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self.length - self.index0')
			self.parser.precode.dedent()
			self.parser.precode.add_line('@property')
			self.parser.precode.add_line('def rindex0(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self.rindex - 1')
			self.parser.precode.dedent()
			self.parser.precode.add_line('def __iter__(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('return self')
			self.parser.precode.dedent()
			self.parser.precode.add_line('def __next__(self):')
			self.parser.precode.indent()
			self.parser.precode.add_line('self.index0 += 1')
			self.parser.precode.add_line('if self.index > self.length:')
			self.parser.precode.indent()
			self.parser.precode.add_line('raise StopIteration')
			self.parser.precode.dedent()
			self.parser.precode.add_line('ret = [self]')
			self.parser.precode.add_line('if isinstance(self._iterable[self.index0], (list, tuple)):')
			self.parser.precode.indent()
			self.parser.precode.add_line('ret.extend(self._iterable[self.index0])')
			self.parser.precode.dedent()
			self.parser.precode.add_line('else:')
			self.parser.precode.indent()
			self.parser.precode.add_line('ret.append(self._iterable[self.index0])')
			self.parser.precode.dedent()
			self.parser.precode.add_line('return ret')
			self.parser.precode.dedent()
			self.parser.precode.dedent()

		from . import _check_envs
		if string and string[-1] == ':':
			string = string[:-1]
		parts = string.split(' in ', 1)
		if len(parts) == 1:
			self.parser.raise_ex('Statement "for" expects format: "for var1, var2 in expr"')
		_check_envs({lvar.strip():1 for lvar in parts[0].split(',')})

		# forloop for nesting fors
		nest_fors = self.parser.stack.count('for') - 1 # I am in stack already
		if nest_fors > 0:
			self.parser.code.add_line('forloop{} = forloop'.format(nest_fors))
		self.parser.code.add_line('for forloop, {} in {}({}):'.format(
			parts[0].strip(), NodeFor.LIQUID_FORLOOP_CLASS,
			NodeExpression(self.parser)._parse(parts[1].strip())), self.parser)
		self.parser.code.indent()

	@pop_stack
	def end(self):
		self.parser.code.dedent()
		nest_fors = self.parser.stack.count('for')
		if nest_fors > 0:
			self.parser.code.add_line('forloop = forloop{}'.format(nest_fors))

class NodeCycle(_Node):

	"""Statement cycle {% cycle 1,2,3 %}"""

	@push_history
	def start(self, string):
		if not self.parser.stack or 'for' not in self.parser.stack:
			self.parser.raise_ex("Statement {!r} must be in a for loop".format(self.name))
		string = '({})'.format(string)
		self.parser.code.add_line('{0}({1}[forloop.index0 % len({1})])'.format(
			LIQUID_COMPILED_RR_APPEND, string), self.parser)

class NodeComment(_Node):

	"""
	Node '{% comment ... %} {% endcomment %}'
	"""

	LIQUID_COMMENTS = '_liquid_node_comments'

	@push_both
	def start(self, string):
		"""Start to compile the node"""
		string = string or '#'
		self.prefix = string.split()
		if len(self.prefix) > 2:
			self.parser.raise_ex('Comments can only be wrapped by no more than 2 strings')
		self.parser.code.add_line("{} = []".format(NodeComment.LIQUID_COMMENTS))
		self.parser.code.add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, NodeComment.LIQUID_COMMENTS))
		self.parser.code.add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, NodeComment.LIQUID_COMMENTS))

	@pop_stack
	def end(self):
		"""End node hit"""
		self.parser.code.add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
		self.parser.code.add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))

		# merge broken lines, for example:
		# a {%if x%}
		# b
		# will be compiled as ['a '] ['\n', 'b']
		# without merging, comment sign will be insert after 'a '
		self.parser.code.add_line('{0} = "".join({0}).splitlines(keepends = True)'.format(
			NodeComment.LIQUID_COMMENTS))
		self.parser.code.add_line('for comment in {}:'.format(NodeComment.LIQUID_COMMENTS))
		self.parser.code.indent()
		self.parser.code.add_line('if comment.endswith("\\n"):')
		self.parser.code.indent()
		self.parser.code.add_line('{}({!r} + comment[:-1].lstrip() + {!r} + "\\n")'.format(
			LIQUID_COMPILED_RR_APPEND, self.prefix[0] + ' ',
			(' ' + self.prefix[1]) if len(self.prefix) > 1 else ''))
		self.parser.code.dedent()
		self.parser.code.add_line('else:')
		self.parser.code.indent()
		self.parser.code.add_line('{}({!r} + comment.lstrip() + {!r})'.format(
			LIQUID_COMPILED_RR_APPEND, self.prefix[0] + ' ',
			(' ' + self.prefix[1]) if len(self.prefix) > 1 else ''))
		self.parser.code.dedent()
		self.parser.code.dedent()

		self.parser.code.add_line('del {}'.format(NodeComment.LIQUID_COMMENTS))

class NodePython(_Node):
	"""
	Node '{% python ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		self.parser.code.add_line(string, self.parser)

class NodeFrom(_Node):
	"""
	Node '{% from ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		self.parser.code.add_line('from ' + string, self.parser)

class NodeImport(_Node):
	"""
	Node '{% import ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		self.parser.code.add_line('import ' + string, self.parser)

class NodeUnless(_Node):
	"""
	Node '{% unless %}'
	"""
	@push_both
	def start(self, string):
		"""Start to compile the node"""
		ifnode = NodeIf(self.parser)
		ifnode.start(string, prefix = 'if not (', suffix = ')')
		ifnode.end()
		self.parser.code.indent()

class NodeCase(_Node):
	"""
	Node '{% case ... %} {% endcase %}'
	"""
	LIQUID_CASE_VARNAME = '_liquid_case_var'

	@push_both
	def start(self, string):
		"""Start to compile the node"""
		self.parser.code.add_line('{} = {}'.format(
			NodeCase.LIQUID_CASE_VARNAME, NodeExpression(self.parser)._parse(string)), self.parser)

	@pop_stack
	def end(self):
		"""End node hit"""
		self.parser.code.dedent()
		self.parser.code.add_line('del {}'.format(NodeCase.LIQUID_CASE_VARNAME))

class NodeWhen(_Node):
	"""
	Node '{% when ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not self.parser.stack or self.parser.stack[-1] != 'case':
			self.parser.raise_ex('"when" must be in a "case" statement')
		ifelse = 'if' if self.parser.history[-1] == 'case' else 'elif'
		if self.parser.history[-1] == 'case':
			ifelse = 'if'
		else:
			ifelse = 'elif'
			self.parser.code.dedent()
		self.parser.code.add_line('{} {} == {}:'.format(
			ifelse, NodeCase.LIQUID_CASE_VARNAME, string), self.parser)
		self.parser.code.indent()

class NodeAssign(_Node):
	"""
	Node '{% assign ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		parts = string.split('=', 1)
		if len(parts) == 1:
			self.parser.raise_ex(
				'Statement "assign" should be in format of "assign a, b = x | filter"')
		variables = (part.strip() for part in parts[0].split(','))
		from . import _check_envs
		_check_envs({var:1 for var in variables})
		self.parser.code.add_line('{} = {}'.format(
			parts[0].strip(), NodeExpression(self.parser)._parse(parts[1].strip())), self.parser)

class NodeBreak(_Node):
	"""
	Node '{% break %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if string:
			self.parser.raise_ex('Additional expressions for {!r}'.format(self.name))
		if  not self.parser.stack or \
			not any(stack in ('for', 'while') for stack in self.parser.stack):
			self.parser.raise_ex('Statement "{}" must be in a loop'.format(self.name))
		self.parser.code.add_line(self.name, self.parser)

class NodeContinue(NodeBreak):
	"""
	Node '{% continue %}'
	"""

class NodeCapture(_Node):
	"""
	Node '{% capture ... %} {% endcapture %}'
	"""
	LIQUID_CAPTURES = '_liquid_captures'

	@push_both
	def start(self, string):
		"""Start to compile the node"""
		from . import _check_envs
		_check_envs({string:1})

		self.variable = string

		self.parser.code.add_line("{} = []".format(NodeCapture.LIQUID_CAPTURES))
		self.parser.code.add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, NodeCapture.LIQUID_CAPTURES))
		self.parser.code.add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, NodeCapture.LIQUID_CAPTURES))

	@pop_stack
	def end(self):
		"""End node hit"""
		self.parser.code.add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
		self.parser.code.add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))
		self.parser.code.add_line('{} = ("".join(str(x) for x in {}))'.format(
			self.variable, NodeCapture.LIQUID_CAPTURES))

class NodeIncrement(_Node):
	"""
	Node '{% increment ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not string:
			self.parser.raise_ex('No variable specified for {!r}'.format(self.name))
		self.parser.code.add_line('{} += 1'.format(string), self.parser)

class NodeDecrement(_Node):
	"""
	Node '{% decrement ... %}'
	"""
	@push_history
	def start(self, string):
		"""Start to compile the node"""
		if not string:
			self.parser.raise_ex('No variable specified for {!r}'.format(self.name))
		self.parser.code.add_line('{} -= 1'.format(string), self.parser)

class NodeWhile(NodeIf):
	"""
	Node '{% while ... %} {% endwhile %}'
	"""
	def start(self, string, prefix = 'while ', suffix = ''):
		"""Start to compile the node"""
		super().start(string, prefix, suffix)
