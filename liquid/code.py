"""Code object for liquidpy"""
from contextlib import contextmanager
import attr
from .exceptions import LiquidCodeTagExists

@attr.s(slots=True, str=False, repr=False)
class LiquidLine:
    """@API
    Line of compiled code

    @params:
        line (str): The line in string format
        context (diot.Diot): The context object
            - filename: The filename
            - lineno: The line number in template source
            - <other context> may not be used in this object
        ndent (int): The indentation level of this line
    """
    line = attr.ib()
    context = attr.ib(default=None, eq=False, repr=False)
    ndent = attr.ib(default=0)
    lineno = attr.ib(init=False)
    filename = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.lineno = self.context and self.context.lineno
        self.filename = self.context and self.context.filename

    def __repr__(self):
        """Get the repr of the object"""
        if self.filename and self.lineno:
            return (f"<LiquidLine {self.line!r} (compiled from "
                    f"{self.filename}:{self.lineno})>")
        return f"<LiquidLine {self.line!r}>"

    def __str__(self):
        """Stringify the object"""
        dent = " " * 2 * self.ndent
        return f"{dent}{self.line}\n"

class LiquidCode:
    """@API
    Build source code conveniently.
    """

    INDENT_STEP = 1

    def __init__(self, indent=0):
        """@API
        Constructor of code builder
        @params:
            indent (int): The initial indent level
        """
        self.codes = []
        self.ndent = indent
        self.tags = {}

    @contextmanager
    def tag(self, codetag):
        """@API
        Make sure the code with the given tag only added once
        @params:
            codetag (str): The tag of the codes to be added
        """
        if codetag in self.tags:
            raise LiquidCodeTagExists()
        # add_code indentation takes no effect on added code,
        # so we need to initiate the indentation
        tagged = LiquidCode(self.ndent)
        self.tags[codetag] = tagged
        tagged.add_line("")
        tagged.add_line(f"# TAGGED CODE: {codetag}")
        yield tagged
        tagged.add_line(f"# ENDED TAGGED CODE")
        tagged.add_line("")
        self.add_code(tagged)

    def __str__(self):
        """@API
        Concatnate of the codes
        @returns:
            The concatnated string
        """
        return "".join(str(c) for c in self.codes)

    def add_line(self, line, context=None):
        """@API
        Add a line of source to the code.
        Indentation and newline will be added for you, don't provide them.
        @params:
            line (str): The line to add
        """
        if not isinstance(line, LiquidLine):
            line = LiquidLine(line, context)
        line.ndent = self.ndent
        self.codes.append(line)

    def add_code(self, code):
        """@API
        Add a LiquidCode object to the code.
        Indentation and newline will be added for you, don't provide them.
        @params:
            code (LiquidCode): The LiquidCode object to add
        """
        assert isinstance(code, LiquidCode), "Expect a LiquidCode object."
        code.ndent += self.ndent
        self.codes.append(code)

    def indent(self):
        """@API
        Increase the current indent for following lines.
        """
        self.ndent += LiquidCode.INDENT_STEP

    def dedent(self):
        """@API
        Decrease the current indent for following lines.
        """
        self.ndent -= LiquidCode.INDENT_STEP

    def get_line(self, lineno):
        """@API
        Get the line with lineno (0-based)
        @params:
            lineno: The line number
        @returns:
            (LiquidLine): The line at `lineno`
        """
        index = 0
        for line in self.codes:
            if isinstance(line, LiquidLine):
                if index < lineno:
                    index += 1
                    continue
                return line
            ret = line.get_line(lineno - index)
            if isinstance(ret, LiquidLine):
                return ret
            index += ret
        return index
