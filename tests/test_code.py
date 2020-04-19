from contextlib import suppress
import pytest
from diot import Diot
from liquid.code import LiquidCode, LiquidLine
from liquid.exceptions import LiquidCodeTagExists

def test_line():
    line = LiquidLine('abc')
    assert line.line == 'abc'
    assert line.filename is None
    assert line.lineno is None
    assert line.ndent == 0

    assert line == LiquidLine('abc')
    assert line != LiquidLine('abc', ndent=1)
    assert line != 'abc'

    assert repr(line) == "<LiquidLine 'abc'>"
    assert str(line) == "abc\n"

    line = LiquidLine('abc', context=Diot(filename='file', lineno=2))
    assert repr(line) == "<LiquidLine 'abc' (compiled from file:2)>"

def test_code_init():
    code = LiquidCode()
    assert code.ndent == 0
    assert code.tags == {}

def test_code_tag():
    code = LiquidCode(1)
    for i in range(3):
        with suppress(LiquidCodeTagExists), code.tag('unique') as tagged:
            tagged.add_line('Some unique shared codes')
    assert str(code).count('  Some unique shared codes') == 1

def test_add_code():

    code = LiquidCode(1)
    subcode = LiquidCode()
    code.add_code(subcode)
    subcode.add_line('1')
    subcode.indent()
    subcode.add_line('2')
    subcode.dedent()
    subcode.add_line('3')
    assert '  1' in str(code).splitlines()
    assert '    2' in str(code).splitlines()
    assert '  3' in str(code).splitlines()

def test_get_line():
    code = LiquidCode()
    shared = LiquidCode()
    code.add_code(shared)
    shared.add_line('')
    shared.add_line('###### SHARED CODE STARTED ######')
    shared.add_line('code0_shared')
    code.add_line('###### SHARED CODE ENDED ######')
    code.add_line('')
    for i in range(3):
        code.add_line(f"code0_line_{i}")

    code1 = LiquidCode()
    shared1 = LiquidCode()
    code1.add_code(shared1)
    code1.add_line('###### SHARED CODE ENDED ######')
    code1.add_line('')
    code.add_code(code1)
    for i in range(3):
        code1.add_line(f"code1_line_{i}")
    shared1.add_line('')
    shared1.add_line('###### SHARED CODE STARTED ######')
    shared1.add_line("code1_shared")

    #print(str(code))
    """
    0.                                      <- code.shared
    1.  ###### SHARED CODE STARTED ######   <- code.shared
    2.  code0_shared                        <- code.shared
    3.  ###### SHARED CODE ENDED ######     <- code
    4.                                      <- code
    5.  code0_line_0                        <- code
    6.  code0_line_1                        <- code
    7.  code0_line_2                        <- code
    8.                                      <- code1.shared
    9.  ###### SHARED CODE STARTED ######   <- code1.shared
    10. code1_shared                        <- code1.shared
    11. ###### SHARED CODE ENDED ######     <- code1
    12.                                     <- code1
    13. code1_line_0                        <- code1
    14. code1_line_1                        <- code1
    15. code1_line_2                        <- code1
    """
    assert str(code.get_line(0))  == "\n"
    assert str(code.get_line(1))  == "###### SHARED CODE STARTED ######\n"
    assert str(code.get_line(2))  == "code0_shared\n"
    assert str(code.get_line(3))  == "###### SHARED CODE ENDED ######\n"
    assert str(code.get_line(4))  == "\n"
    assert str(code.get_line(5))  == "code0_line_0\n"
    assert str(code.get_line(6))  == "code0_line_1\n"
    assert str(code.get_line(7))  == "code0_line_2\n"
    assert str(code.get_line(8))  == "\n"
    assert str(code.get_line(9))  == "###### SHARED CODE STARTED ######\n"
    assert str(code.get_line(10))  == "code1_shared\n"
    assert str(code.get_line(11)) == "###### SHARED CODE ENDED ######\n"
    assert str(code.get_line(12)) == "\n"
    assert str(code.get_line(13)) == "code1_line_0\n"
    assert str(code.get_line(14)) == "code1_line_1\n"
    assert str(code.get_line(15)) == "code1_line_2\n"

def test_get_line2():
    # code in code
    code1 = LiquidCode()
    code2 = LiquidCode()
    code3 = LiquidCode()
    code1.add_line("0")
    code1.add_line("1")
    code1.add_line("2")
    code1.add_code(code2)
    code2.add_line("3")
    code2.add_line("4")
    code2.add_line("5")
    code2.add_code(code3)
    code3.add_line("6")
    code3.add_line("7")
    code2.add_line("8")
    code2.add_line("9")
    code1.add_line("10")
    assert str(code1.get_line(0))   == "0\n"
    assert str(code1.get_line(1))   == "1\n"
    assert str(code1.get_line(2))   == "2\n"
    assert str(code1.get_line(3))   == "3\n"
    assert str(code1.get_line(4))   == "4\n"
    assert str(code1.get_line(5))   == "5\n"
    assert str(code1.get_line(6))   == "6\n"
    assert str(code1.get_line(7))   == "7\n"
    assert str(code1.get_line(8))   == "8\n"
    assert str(code1.get_line(9))   == "9\n"
    assert str(code1.get_line(10))  == "10\n"


# def test_replace():
#     code = LiquidCode(1)
#     subcode = LiquidCode(indent = 1)
#     code.add_code(subcode)
#     assert subcode.ndent == 2
#     assert subcode.shared.ndent == 2
#     subcode2 = LiquidCode()
#     subcode.replace(subcode2)
#     assert subcode2.ndent == 2
#     assert subcode2.shared.ndent == 2

#     subcode2.add_line('1')
#     subcode2.shared.indent()
#     subcode2.shared.add_line('2')
#     subcode2.shared.dedent()
#     subcode2.shared.add_line('3')
#     assert '    1' in str(code).splitlines()
#     assert '      2' in str(code).splitlines()
#     assert '    3' in str(code).splitlines()
