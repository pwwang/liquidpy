import pytest

from liquid.tags.grammar import Grammar

def test_update():
    grammar = Grammar('!abc: NAME\n%ignore WS NEWLINE')
    grammar.update('%ignore WS NEWLINE')

    assert str(grammar) == '!abc: NAME\n\n%ignore WS NEWLINE\n'

    with pytest.raises(AssertionError):
        grammar.update('?abc: NAME')

    grammar.update('!abc: NAME1\n  | NAME2')
    assert str(
        grammar
    ) == '!abc: NAME\n    | NAME1\n    | NAME2\n\n%ignore WS NEWLINE\n'

def test_replace():
    grammar = Grammar('')
    grammar.replace('add', 'NAME')
    assert str(grammar) == 'add: NAME\n\n'

def test_add_to():
    grammar = Grammar('')
    grammar.replace('add', 'NAME')
    grammar.add_to('add', 'NAME1')
    assert str(
        grammar
    ) == 'add: NAME\n    | NAME1\n\n'
