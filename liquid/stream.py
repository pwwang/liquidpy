"""
Stream helper for liquidpy
"""
import io
from .defaults import LIQUID_DEBUG_SOURCE_CONTEXT

def words_to_matrix(words):
	"""
	Convert words to matrix for searching.
	For example:
	```
	['{%', '{%-', '{{'] => [
		{'{': 0},     3 shares, 0 endings
		{'%': 1, '{': 1},
		{'-': 1}
	]
	```
	@params:
		words: The words to be converted
	@returns:
		The converted matrix
	"""
	matrix = [{} for _ in range(max(len(word) for word in words))]
	for word in words:
		for i, char in enumerate(word):
			matrix[i].setdefault(char, 0)
			if i == len(word) - 1:
				matrix[i][char] += 1
	return matrix

class LiquidStream:
	"""
	The stream helper for liquidpy
	"""
	def __init__(self, stream):
		"""
		Initialize the stream
		@params:
			stream (Stream): A python stream
		"""
		self.stream = stream
		self.cursor = stream.tell()

	@staticmethod
	def from_file(path):
		"""
		Get stream of a file
		@params:
			path (str): The path of the file
		@returns:
			LiquidStream
		"""
		return LiquidStream(io.open(path, mode = 'r', encoding = 'utf-8'))

	@staticmethod
	def from_string(string):
		"""
		Get stream of a string
		@params:
			string (str): The string
		@returns:
			LiquidStream
		"""
		return LiquidStream(io.StringIO(string))

	@staticmethod
	def from_stream(stream):
		"""
		Get stream of a stream
		@params:
			stream (Stream): A stream
		@returns:
			LiquidStream
		"""
		return LiquidStream(stream)

	def __del__(self):
		"""
		Close the stream when GC
		"""
		self.close()

	def close(self):
		"""
		Close the stream
		"""
		if self.stream and not self.stream.closed:
			self.stream.close()

	def next(self):
		"""
		Read next character from the stream
		@returns:
			str: the next character
		"""
		ret = self.stream.read(1)
		self.cursor += len(ret.encode('utf-8'))
		return ret

	def back(self):
		"""
		Put cursor 1-character back
		"""
		self.cursor -= 1
		self.stream.seek(self.cursor)

	def rewind(self):
		"""
		Rewind the stream
		"""
		self.stream.seek(0)
		self.cursor = 0

	def eos(self):
		"""
		Tell if the stream is ended
		@returns:
			`True` if it is else `False`
		"""
		nchar = self.next()
		if not nchar:
			return True
		self.cursor -= 1
		self.stream.seek(self.cursor)
		return False

	def dump(self):
		"""
		Dump the rest of the stream
		@returns:
			str: The rest of the stream
		"""
		return self.stream.read()

	def readline(self):
		"""Read a single line from the stream"""
		return self.stream.readline()

	def get_context(self, lineno, context = LIQUID_DEBUG_SOURCE_CONTEXT, baselineno = 1):
		"""
		Get the line of source code and its context
		@params:
			lineno  (int): Line number of current line
			context (int): How many lines of context to show
		@returns:
			list: The formated code with context
		"""
		self.rewind()
		ret     = []
		maxline = lineno + context
		nbit    = len(str(maxline)) + 1
		i       = baselineno
		line    = self.readline()
		while line:
			if i < lineno - context or i > maxline:
				pass
			else:
				ret.append("{} {} {}".format(
					'>' if i == lineno else  ' ', (str(i) + '.').ljust(nbit), line.rstrip()))
			i += 1
			line = self.readline()
		return ret

	def split(self, delimiter, limit = 0, trim = True,
		wraps = None, quotes = '"\'`', escape = '\\'):
		"""
		Split the string of the stream
		@params:
			delimiter (str): The delimiter
			limit (int): The max limit of the split
			trim (bool): Whether to trim each part or not
			wraps (list): A list of paired wraps to skip of the delimiter is wrapped by them
			quotes (str): A series of quotes to skip of the delimiter is wrapped by them
			escape (str): The escape character to see if any character is escaped
		@returns:
			list: The split strings
		"""
		wraps = ['{}', '[]', '()'] if wraps is None else wraps
		preceding, stop = self.until([delimiter], False, wraps, quotes, escape)
		ret = [preceding.strip() if trim else preceding]
		nsplit = 0
		while stop:
			nsplit += 1
			if limit and nsplit >= limit:
				rest = self.dump()
				ret.append(rest.strip() if trim else rest)
				break
			preceding, stop = self.until([delimiter], False, wraps, quotes, escape)
			ret.append(preceding.strip() if trim else preceding)
		return ret

	def until(self, words, greedy = True, wraps = None, quotes = '"\'`', escape = '\\'):
		"""
		Get the string until certain words
		For example:
		```
		s = LiquidStream.from_string("abcdefgh")
		s.until(["f", "fg"]) == "abcde", "fg"
		# cursor point to 'h'
		s.until(["f", "fg"], greedy = False) == "abcde", "f"
		# cursor point to 'g'
		s.until(["x", "xy"]) == "abcdefg", ""
		# cursor point to eos
		```
		@params:
			words (list): A list of words to search
			greedy (bool): Whether do a greedy search or not
				- Only effective when the words have prefices in common. For example
				- ['abc', 'ab'], then abc will be matched first
			wraps (list): A list of paired wraps to skip of the delimiter is wrapped by them
			quotes (str): A series of quotes to skip of the delimiter is wrapped by them
			escape (str): The escape character to see if any character is escaped
		@returns:
			str: The string that has been searched
			str: The matched word
		"""
		# pylint:disable=too-many-locals,too-many-nested-blocks,too-many-branches
		wraps = ['{}', '[]', '()'] if wraps is None else wraps
		ret               = ''
		matrix            = words_to_matrix(words)
		len_matrix        = len(matrix)
		matched_chars     = ''
		matched_candidate = None
		wrap_opens        = {wrap[0]:i for i, wrap in enumerate(wraps)
			if  not any(wrap[0] in mat for mat in matrix) and \
				not any(wrap[1] in mat for mat in matrix)}
		wrap_closes       = {wraps[i][1]:i for wrap_open,i in wrap_opens.items()}
		quote_index       = {quote:i for i, quote in enumerate(quotes)
			if not any(quote in mat for mat in matrix)}
		wrap_flags        = [0 for _ in range(len(wraps))]
		quote_flags       = [False for _ in range(len(quotes))]
		escape_flags      = False
		char              = self.next()
		#print('START', '-' * 10, matrix)
		while True:
			#print(char, end = ' ')
			if not char:
				return ret, matched_candidate
			if char == escape:
				if matched_candidate and escape not in matrix[len(matched_candidate)]:
					self.back()
					return ret, matched_candidate
				escape_flags = not escape_flags
				ret += matched_chars + char
				matched_chars = ''
			elif not escape_flags: # and char != escape
				if char in wrap_opens and not any(quote_flags):
					wrap_flags[wrap_opens[char]] += 1
				elif char in wrap_closes and not any(quote_flags):
					wrap_flags[wrap_closes[char]] -= 1
				elif char in quote_index and \
					not any(flag for i, flag in enumerate(quote_flags) if i != quote_index[char]):
					# make sure I am not quoted
					quote_flags[quote_index[char]] = not quote_flags[quote_index[char]]
				if sum(wrap_flags) > 0 or any(quote_flags):
					if matched_candidate:
						self.back()
						return ret, matched_candidate
					ret += matched_chars + char
					matched_chars = ''
				else:
					len_matched_chars = len(matched_chars)
					matching_dict = matrix[len_matched_chars]
					#print(' ', len_matched_chars, matching_dict)
					if char in matching_dict:
						matched_chars += char
						endings = matching_dict[char]
						if not greedy and endings:
							return ret, matched_chars
						if endings:
							matched_candidate = matched_chars
							#print('mm', matched_candidate)
							if len_matched_chars + 1 == len_matrix: # we have matched all chars
								return ret, matched_chars

					elif matched_candidate:
						self.back()
						return ret, matched_candidate
					else:
						ret += matched_chars + char
						matched_chars = ''
			else: # char == escape or escape_flags
				escape_flags = False
				ret += matched_chars + char
				matched_chars = ''

			char = self.next()
