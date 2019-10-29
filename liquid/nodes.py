import logging
from .stream import Stream
from .filters import liquid_filters
from .exceptions import LiquidSyntaxError
from .defaults import LIQUID_LOGGER_NAME, LIQUID_MODES, \
	LIQUID_LIQUID_FILTERS, LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RR_EXTEND, \
	LIQUID_COMPILED_RENDERED


def pushstack(func):
	def retfunc(self, *args, **kwargs):
		self.meta['stack'].append(self.name)
		func(self, *args, **kwargs)
	return retfunc

def popstack(func):
	def retfunc(self, *args, **kwargs):
		last = self.meta['stack'] and self.meta['stack'].pop() or None
		if last != self.name:
			if last:
				self.meta['raise'](
					"Unmatched end tag: 'end{}', expect 'end{}'".format(self.name, last))
			self.meta['raise']("Unmatched end tag: 'end{}'".format(self.name))
		func(self, *args, **kwargs)
	return retfunc

def dedent(func):
	def retfunc(self, *args, **kwargs):
		func(self, *args, **kwargs)
		self.meta['code'].dedent()
	return retfunc

class _Node:

	def __init__(self, meta):
		self.meta = meta
		self.name = self.__class__.__name__[4:].lower()

	def start(self, string, lineno):
		"""Start to parse the node"""

	@popstack
	@dedent
	def end(self):
		pass

class NodeMode(_Node):

	def _set_mode(self, mode):
		if mode not in LIQUID_MODES:
			self.meta['raise']('Not a valid mode: {!r}'.format(mode))
		self.meta['mode'] = mode

	def _set_loglevel(self, loglevel):
		loglevel = loglevel.upper()
		if not NodeMode._is_loglevel(loglevel):
			self.meta['raise']('Not a valid loglevel: {!r}'.format(loglevel))
		logging.getLogger(LIQUID_LOGGER_NAME).setLevel(loglevel)

	@staticmethod
	def _is_loglevel(loglevel):
		return isinstance(logging.getLevelName(loglevel), int)

	def start(self, string, lineno):
		if not string:
			raise LiquidSyntaxError('Expecting a mode value')
		parts = string.split()
		if len(parts) == 1:
			parts = parts[0].split(',')
		parts  = [part.strip() for part in parts]
		if len(parts) > 2:
			raise LiquidSyntaxError('Mode can only take at most 2 values')

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

	@pushstack
	def start(self, string, lineno, prefix = 'if ', suffix = ''):
		if not string:
			self.meta['raise']('No expressions for statement "{}"'.format(self.name))
		sstream = Stream.from_string(string)
		# merge multiple lines
		sstream = Stream.from_string(' '.join(sstream.split(['\\\n'])))
		prestr, bracket = sstream.until(['`'])
		ifexpr = prefix
		if not bracket:
			ifexpr += prestr
		while bracket:
			expr, endbrkt = sstream.until(['`'])

			if endbrkt:
				ifexpr += prestr + NodeExpression(self.meta)._parse(expr)
				prestr, bracket = sstream.until(['`'])
				if not bracket:
					ifexpr += prestr
			else: # pragma: no cover
				# this technically will not  happen
				# because if there is only on `, there should be a syntax error
				ifexpr += prestr + '`' + expr + endbrkt
				bracket = ''
		ifexpr = (ifexpr[:-1] if ifexpr[-1] == ':' else ifexpr) + suffix
		self.meta['code'].add_line(ifexpr + ':', lineno)
		self.meta['code'].indent()

class NodeElse(_Node):

	def start(self, string, lineno):
		if not self.meta['stack'] or self.meta['stack'][-1] not in ('case', 'if', 'unless'):
			self.meta['raise']('"else" must be in an if/unless/case statement')
		# see if it is else if
		parts = string.split(maxsplit = 1)
		if not parts:
			self.meta['code'].dedent()
			self.meta['code'].add_line('else:')
			self.meta['code'].indent()
		elif parts[0] == 'if' and self.meta['stack'][-1] == 'if':
			ifnode = NodeIf(self.meta)
			self.meta['code'].dedent()
			ifnode.start(parts[1] if len(parts) > 1 else '', lineno, 'elif ')
			ifnode.end()
			self.meta['code'].indent()
		else:
			self.meta['raise']('"else" should not be followed by any expressions')

class NodeElseif(_Node):

	def start(self, string, lineno):
		if not self.meta['stack'] or self.meta['stack'][-1] != 'if':
			self.meta['raise']('"elseif/elif/elsif" must be in an "if/unless" statement')
		ifnode = NodeIf(self.meta)
		self.meta['code'].dedent()
		ifnode.start(string, lineno, 'elif ')
		ifnode.end()
		self.meta['code'].indent()

NodeElif = NodeElsif = NodeElseif

class NodeLiteral(_Node):

	def start(self, string, lineno):
		if not string:
			return
		lines = string.splitlines(keepends = True)
		if len(lines) > 1:
			self.meta['code'].add_line('{}(['.format(LIQUID_COMPILED_RR_EXTEND))
			self.meta['code'].indent()
			for i, line in enumerate(lines):
				self.meta['code'].add_line('{!r},'.format(line), lineno + i)
			self.meta['code'].dedent()
			self.meta['code'].add_line('])')
		else:
			self.meta['code'].add_line('{}({!r})'.format(
				LIQUID_COMPILED_RR_APPEND, lines[0]), lineno)

NodeRaw = NodeLiteral

class NodeExpression(_Node):

	LIQUID_DOT_FUNC_NAME = '_liquid_dodots_function'

	@staticmethod
	def _parse_base(expr, single = False):
		"""
		Parse the first part of an expression
		"""
		if single:
			dots = Stream.from_string(expr).split('.')
			# in case we have a float number
			# 1.2 or 1.3e-10
			ret = dots.pop(0)
			if ret.isdigit() and dots and dots[0].isdigit():
				ret = ret + '.' + dots.pop(0)

			for dot in dots:
				dstream = Stream.from_string(dot)
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

		parts = Stream.from_string(expr).split(',')
		# if we can split, ok, we have removed all redundant ()
		if len(parts) > 1:
			return '({})'.format(', '.join(NodeExpression._parse_base(part, single = True)
				for part in parts))
		elif minbrkt > 0:
			# if we cannot, like (1), (1,2), ((1,2), [3,4]), try to remove the bracket again ->
			#   "1", "1,2", "(1,2), [3,4]"
			parts = Stream.from_string(expr[1:-1]).split(',')
			if len(parts) > 1:
				return '({})'.format(', '.join(NodeExpression._parse_base(part, single = True)
					for part in parts))
		return NodeExpression._parse_base(parts[0], single = True)

	def _parse_filter(self, expr, args):
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
		estream  = Stream.from_string(expr)
		eparts   = estream.split(':', limit = 1)
		base     = None
		is_tuple = args[0] == '(' and args[-1] == ')'
		star     = liquid  = ''
		if '*' in expr[:2]:
			star = True
		argprefix = '*' if is_tuple and star else ''
		if '@' in expr[:2]:
			liquid = True
		eparts[0] = eparts[0].lstrip('*@')
		if not eparts[0]:
			eparts[0] = 'lambda _'

		if eparts[0][0] in ('.', '['):
			if star or liquid:
				raise self.meta['raise']('Attribute filter should not have modifiers')
			base = NodeExpression._parse_base(args + eparts[0], single = True)

		if liquid and eparts[0] not in liquid_filters:
			raise self.meta['raise']("Unknown liquid filter: '@{}'".format(eparts[0]))
		filter_name = '{}[{!r}]'.format(LIQUID_LIQUID_FILTERS, eparts[0]) if liquid else eparts[0]

		if len(eparts) == 2:
			if base: # 2, 4, 5
				return '{}({})'.format(base, eparts[1])
			if eparts[0].startswith('lambda '): # 8, 9
				return '({}: ({}))({}{})'.format(eparts[0], eparts[1], argprefix, args)
			# 6, 7
			fastream = Stream.from_string(eparts[1])
			faparts = fastream.split(',')
			if len(faparts) == 1 and not faparts[0]:
				faparts = ['_']

			found_args = False
			if not found_args:
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
		elif base: # 1, 3
			return base
		else: # 10
			return '{}({})'.format(filter_name, argprefix + args)

	def _parse(self, string):
		#if not string: # Empty node
		#	self.meta['raise']('Nothing found for expression')

		if 	not hasattr(self.meta['precode'], NodeExpression.LIQUID_DOT_FUNC_NAME) or \
			not getattr(self.meta['precode'], NodeExpression.LIQUID_DOT_FUNC_NAME):
			setattr(self.meta['precode'], NodeExpression.LIQUID_DOT_FUNC_NAME, True)
			self.meta['precode'].add_line('def {}(obj, dot):'.format(NodeExpression.LIQUID_DOT_FUNC_NAME))
			self.meta['precode'].indent()
			self.meta['precode'].add_line('try:')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return getattr(obj, dot)')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('except (AttributeError, TypeError):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return obj[dot]')
			self.meta['precode'].dedent()
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('')

		sstream = Stream.from_string(string)
		exprs   = sstream.split('|')
		value   = NodeExpression._parse_base(exprs[0])

		for expr in exprs[1:]:
			if not expr:
				self.meta['raise']('No filter specified')
			value = self._parse_filter(expr, value)
		return value

	def start(self, string, lineno):
		self.meta['code'].add_line('{}({})'.format(
			LIQUID_COMPILED_RR_APPEND, self._parse(string)), lineno)

class NodeFor(_Node):
	LIQUID_FORLOOP_CLASS = '_Liquid_forloop_class'

	@pushstack
	def start(self, string, lineno):
		# i, v in x | range

		if  not hasattr(self.meta['precode'], NodeFor.LIQUID_FORLOOP_CLASS) or \
			not getattr(self.meta['precode'], NodeFor.LIQUID_FORLOOP_CLASS):
			setattr(self.meta['precode'], NodeFor.LIQUID_FORLOOP_CLASS, True)

			self.meta['precode'].add_line('class {}:'.format(NodeFor.LIQUID_FORLOOP_CLASS))
			self.meta['precode'].indent()
			self.meta['precode'].add_line('def __init__(self, iterable):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('self._iterable = [it for it in iterable]')
			self.meta['precode'].add_line('self.index0 = -1')
			self.meta['precode'].add_line('self.length = len(self._iterable)')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('@property')
			self.meta['precode'].add_line('def first(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self.index0 == 0')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('@property')
			self.meta['precode'].add_line('def last(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self.index == self.length')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('@property')
			self.meta['precode'].add_line('def index(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self.index0 + 1')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('@property')
			self.meta['precode'].add_line('def rindex(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self.length - self.index0')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('@property')
			self.meta['precode'].add_line('def rindex0(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self.rindex - 1')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('def __iter__(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('return self')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('def __next__(self):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('self.index0 += 1')
			self.meta['precode'].add_line('if self.index > self.length:')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('raise StopIteration')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('ret = [self]')
			self.meta['precode'].add_line('if isinstance(self._iterable[self.index0], (list, tuple)):')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('ret.extend(self._iterable[self.index0])')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('else:')
			self.meta['precode'].indent()
			self.meta['precode'].add_line('ret.append(self._iterable[self.index0])')
			self.meta['precode'].dedent()
			self.meta['precode'].add_line('return ret')
			self.meta['precode'].dedent()
			self.meta['precode'].dedent()

		from . import _check_envs
		if string and string[-1] == ':':
			string = string[:-1]
		parts = string.split('in', 1)
		if len(parts) == 1:
			self.meta['raise']('Statement "for" expects format: "for var1, var2 in expr"')
		_check_envs({lvar.strip():1 for lvar in parts[0].split(',')})

		self.meta['code'].add_line('for forloop, {} in {}({}):'.format(
			parts[0].strip(), NodeFor.LIQUID_FORLOOP_CLASS,
			NodeExpression(self.meta)._parse(parts[1].strip())))
		self.meta['code'].indent()

class NodeComment(_Node):

	LIQUID_COMMENTS = '_liquid_node_comments'

	@pushstack
	def start(self, string, lineno):
		string = string or '#'
		self.prefix = string.split()
		if len(self.prefix) > 2:
			self.meta['raise']('Comments can only be wrapped by no more than 2 strings')
		self.meta['code'].add_line("{} = []".format(NodeComment.LIQUID_COMMENTS))
		self.meta['code'].add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, NodeComment.LIQUID_COMMENTS))
		self.meta['code'].add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, NodeComment.LIQUID_COMMENTS))

	@popstack
	def end(self):
		self.meta['code'].add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
		self.meta['code'].add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))

		# merge broken lines, for example:
		# a {%if x%}
		# b
		# will be compiled as ['a '] ['\n', 'b']
		# without merging, comment sign will be insert after 'a '
		self.meta['code'].add_line('{0} = "".join({0}).splitlines(keepends = True)'.format(
			NodeComment.LIQUID_COMMENTS))
		self.meta['code'].add_line('for comment in {}:'.format(NodeComment.LIQUID_COMMENTS))
		self.meta['code'].indent()
		self.meta['code'].add_line('if comment.endswith("\\n"):')
		self.meta['code'].indent()
		self.meta['code'].add_line('{}({!r} + comment[:-1].lstrip() + {!r} + "\\n")'.format(
			LIQUID_COMPILED_RR_APPEND, self.prefix[0] + ' ',
			(' ' + self.prefix[1]) if len(self.prefix) > 1 else ''))
		self.meta['code'].dedent()
		self.meta['code'].add_line('else:')
		self.meta['code'].indent()
		self.meta['code'].add_line('{}({!r} + comment.lstrip() + {!r})'.format(
			LIQUID_COMPILED_RR_APPEND, self.prefix[0] + ' ',
			(' ' + self.prefix[1]) if len(self.prefix) > 1 else ''))
		self.meta['code'].dedent()
		self.meta['code'].dedent()

		self.meta['code'].add_line('del {}'.format(NodeComment.LIQUID_COMMENTS))

class NodePython(_Node):

	def start(self, string, lineno):
		self.meta['code'].add_line(string)

class NodeFrom(_Node):

	def start(self, string, lineno):
		self.meta['code'].add_line('from ' + string)

class NodeImport(_Node):

	def start(self, string, lineno):
		self.meta['code'].add_line('import ' + string)

class NodeUnless(_Node):

	@pushstack
	def start(self, string, lineno):
		ifnode = NodeIf(self.meta)
		ifnode.start(string, lineno, prefix = 'if not (', suffix = ')')
		ifnode.end()
		self.meta['code'].indent()

class NodeCase(_Node):
	LIQUID_CASE_VARNAME = '_liquid_case_var'

	@pushstack
	def start(self, string, lineno):
		self.meta['code'].add_line('{} = {}'.format(
			NodeCase.LIQUID_CASE_VARNAME, NodeExpression(self.meta)._parse(string)))
		self.meta['case_started'] = True

	@popstack
	def end(self):
		del self.meta['case_started']
		self.meta['code'].dedent()
		self.meta['code'].add_line('del {}'.format(NodeCase.LIQUID_CASE_VARNAME))

class NodeWhen(_Node):

	def start(self, string, lineno):
		if not self.meta['stack'] or self.meta['stack'][-1] != 'case':
			self.meta['raise']('"when" must be in a "case" statement')
		if self.meta.get('case_started'):
			self.first = True
			self.meta['case_started'] = False
		else:
			self.first = False

		ifelse = 'if' if self.first else 'elif'
		if not self.first:
			self.meta['code'].dedent()
		self.meta['code'].add_line('{} {} == {}:'.format(
			ifelse, NodeCase.LIQUID_CASE_VARNAME, string))
		self.meta['code'].indent()

class NodeAssign(_Node):

	def start(self, string, lineno):
		parts = string.split('=', 1)
		if len(parts) == 1:
			self.meta['raise'](
				'Statement "assign" should be in format of "assign a, b = x | filter"')
		variables = (part.strip() for part in parts[0].split(','))
		from . import _check_envs
		_check_envs({var:1 for var in variables})
		self.meta['code'].add_line('{} = {}'.format(
			parts[0].strip(), NodeExpression(self.meta)._parse(parts[1].strip())), lineno)

class NodeBreak(_Node):

	def start(self, string, lineno):
		if string:
			self.meta['raise']('Additional expressions for {!r}'.format(self.name))
		if  not self.meta['stack'] or \
			not any(stack in ('for', 'while') for stack in self.meta['stack']):
			self.meta['raise']('Statement "{}" must be in a loop'.format(self.name))
		self.meta['code'].add_line(self.name)

class NodeContinue(NodeBreak):
	pass

class NodeCapture(_Node):

	LIQUID_CAPTURES = '_liquid_captures'

	@pushstack
	def start(self, string, lineno):
		from . import _check_envs
		_check_envs({string:1})

		self.variable = string

		self.meta['code'].add_line("{} = []".format(NodeCapture.LIQUID_CAPTURES))
		self.meta['code'].add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, NodeCapture.LIQUID_CAPTURES))
		self.meta['code'].add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, NodeCapture.LIQUID_CAPTURES))

	@popstack
	def end(self):
		self.meta['code'].add_line("{} = {}.append".format(
			LIQUID_COMPILED_RR_APPEND, LIQUID_COMPILED_RENDERED))
		self.meta['code'].add_line("{} = {}.extend".format(
			LIQUID_COMPILED_RR_EXTEND, LIQUID_COMPILED_RENDERED))
		self.meta['code'].add_line('{} = ("".join(str(x) for x in {}))'.format(
			self.variable, NodeCapture.LIQUID_CAPTURES))

class NodeIncrement(_Node):

	def start(self, string, lineno):
		if not string:
			self.meta['raise']('No variable specified for {!r}'.format(self.name))
		self.meta['code'].add_line('{} += 1'.format(string))

class NodeDecrement(_Node):

	def start(self, string, lineno):
		if not string:
			self.meta['raise']('No variable specified for {!r}'.format(self.name))
		self.meta['code'].add_line('{} -= 1'.format(string))

class NodeWhile(NodeIf):

	def start(self, string, lineno, prefix = 'while ', suffix = ''):
		super().start(string, lineno, prefix, suffix)
